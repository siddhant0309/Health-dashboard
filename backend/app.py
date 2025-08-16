from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import time
import json
import os
import hashlib
import jwt
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import threading
import schedule
import logging
from functools import wraps

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///health_dashboard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
SERVICE_HEALTH = Gauge('service_health_status', 'Service health status', ['service_name'])
ERROR_RATE = Counter('service_errors_total', 'Total service errors', ['service_name'])
COST_METRICS = Gauge('service_cost_total', 'Service cost in dollars', ['service_name'])

# Enhanced Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, admin, operator
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='unknown')
    last_check = db.Column(db.Integer, default=datetime.utcnow)
    uptime = db.Column(db.Float, default=0.0)
    response_time = db.Column(db.Float, default=0.0)
    error_count = db.Column(db.Integer, default=0)
    total_checks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_type = db.Column(db.String(50), default='api')  # api, database, storage, etc.
    cost_per_request = db.Column(db.Float, default=0.0001)
    cost_per_gb_hour = db.Column(db.Float, default=0.10)
    alert_thresholds = db.Column(db.JSON)  # Store alert thresholds as JSON
    maintenance_window = db.Column(db.String(100))  # e.g., "Sun 2:00-4:00 UTC"

class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)
    status_code = db.Column(db.Integer)
    error = db.Column(db.Boolean, default=False)
    uptime = db.Column(db.Float)
    cost = db.Column(db.Float, default=0.0)
    request_size = db.Column(db.Integer, default=0)  # Request size in bytes
    response_size = db.Column(db.Integer, default=0)  # Response size in bytes

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolution_notes = db.Column(db.Text)
    sla_target = db.Column(db.DateTime)  # SLA target for resolution
    actual_resolution_time = db.Column(db.Float)  # Time to resolve in hours

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    threshold = db.Column(db.Float)
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    severity = db.Column(db.String(20), default='medium')
    notification_sent = db.Column(db.Boolean, default=False)
    escalation_level = db.Column(db.Integer, default=1)

class Maintenance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed
    type = db.Column(db.String(50), default='planned')  # planned, emergency
    impact_level = db.Column(db.String(20), default='low')  # low, medium, high
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Enhanced health check function with cost calculation
def check_service_health(service):
    """Check the health of a specific service with enhanced metrics"""
    start_time = time.time()
    try:
        response = requests.get(service.url, timeout=10)
        response_time = time.time() - start_time
        status_code = response.status_code
        
        # Calculate costs
        request_size = len(str(request.headers).encode('utf-8'))
        response_size = len(response.content)
        cost = service.cost_per_request + (response_size / (1024**3)) * service.cost_per_gb_hour
        
        # Update service status
        if status_code == 200:
            service.status = 'healthy'
            service.uptime = 100.0
        else:
            service.status = 'degraded'
            service.uptime = 50.0
            
        service.response_time = response_time
        service.last_check = datetime.utcnow()
        service.total_checks += 1
        
        # Record enhanced metric
        metric = Metric(
            service_id=service.id,
            response_time=response_time,
            status_code=status_code,
            error=False,
            uptime=service.uptime,
            cost=cost,
            request_size=request_size,
            response_size=response_size
        )
        db.session.add(metric)
        
        # Update Prometheus metrics
        SERVICE_HEALTH.labels(service_name=service.name).set(1 if service.status == 'healthy' else 0)
        COST_METRICS.labels(service_name=service.name).set(cost)
        
        # Check alert thresholds
        check_alert_thresholds(service, response_time, status_code, cost)
        
    except Exception as e:
        response_time = time.time() - start_time
        service.status = 'down'
        service.uptime = 0.0
        service.response_time = response_time
        service.last_check = datetime.utcnow()
        service.error_count += 1
        service.total_checks += 1
        
        # Record error metric
        metric = Metric(
            service_id=service.id,
            response_time=response_time,
            status_code=0,
            error=True,
            uptime=0.0,
            cost=0.0
        )
        db.session.add(metric)
        
        # Update Prometheus metrics
        SERVICE_HEALTH.labels(service_name=service.name).set(0)
        ERROR_RATE.labels(service_name=service.name).inc()
        
        # Create incident if service is down
        if service.status == 'down':
            incident = Incident(
                service_id=service.id,
                title=f"Service {service.name} is down",
                description=f"Service {service.name} at {service.url} is not responding. Error: {str(e)}",
                severity='high',
                status='open',
                sla_target=datetime.utcnow() + timedelta(hours=4)  # 4-hour SLA
            )
            db.session.add(incident)
    
    db.session.commit()

def check_alert_thresholds(service, response_time, status_code, cost):
    """Check if any alert thresholds have been exceeded"""
    if not service.alert_thresholds:
        return
    
    thresholds = service.alert_thresholds
    
    # Response time threshold
    if 'response_time' in thresholds and response_time > thresholds['response_time']:
        alert = Alert(
            service_id=service.id,
            type='high_response_time',
            message=f'Response time {response_time:.3f}s exceeded threshold {thresholds["response_time"]}s',
            threshold=thresholds['response_time'],
            severity='medium'
        )
        db.session.add(alert)
    
    # Cost threshold
    if 'cost' in thresholds and cost > thresholds['cost']:
        alert = Alert(
            service_id=service.id,
            type='high_cost',
            message=f'Cost ${cost:.6f} exceeded threshold ${thresholds["cost"]:.6f}',
            threshold=thresholds['cost'],
            severity='high'
        )
        db.session.add(alert)
    
    # Error rate threshold
    if 'error_rate' in thresholds:
        error_rate = (service.error_count / service.total_checks) * 100
        if error_rate > thresholds['error_rate']:
            alert = Alert(
                service_id=service.id,
                type='high_error_rate',
                message=f'Error rate {error_rate:.1f}% exceeded threshold {thresholds["error_rate"]}%',
                threshold=thresholds['error_rate'],
                severity='high'
            )
            db.session.add(alert)

# Background health checker
def run_health_checks():
    """Run health checks for all services"""
    with app.app_context():
        services = Service.query.all()
        for service in services:
            try:
                check_service_health(service)
            except Exception as e:
                logger.error(f"Error checking service {service.name}: {e}")

def schedule_health_checks():
    """Schedule health checks every 30 seconds"""
    schedule.every(30).seconds.do(run_health_checks)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start health check scheduler in background
health_check_thread = threading.Thread(target=schedule_health_checks, daemon=True)
health_check_thread.start()

# Enhanced API Routes
@app.route('/api/health')
def health():
    """Overall system health endpoint"""
    REQUEST_COUNT.labels(method='GET', endpoint='/api/health', status=200).inc()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0',
        'phase': 'Phase 2 - Enhanced Monitoring',
        'features': [
            'Advanced cost tracking',
            'Enhanced alerting',
            'Maintenance scheduling',
            'User management',
            'SLA monitoring'
        ]
    })

@app.route('/api/services', methods=['GET'])
@token_required
def get_services(current_user):
    """Get all monitored services"""
    REQUEST_COUNT.labels(method='GET', endpoint='/api/services', status=200).inc()
    services = Service.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'url': s.url,
        'status': s.status,
        'last_check': s.last_check.isoformat() if s.last_check else None,
        'uptime': s.uptime,
        'response_time': s.response_time,
        'error_count': s.error_count,
        'total_checks': s.total_checks,
        'service_type': s.service_type,
        'cost_per_request': s.cost_per_request,
        'cost_per_gb_hour': s.cost_per_gb_hour,
        'alert_thresholds': s.alert_thresholds,
        'maintenance_window': s.maintenance_window
    } for s in services])

@app.route('/api/services', methods=['POST'])
@token_required
def add_service(current_user):
    """Add a new service to monitor"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'url' not in data:
        return jsonify({'error': 'Name and URL are required'}), 400
    
    service = Service(
        name=data['name'],
        url=data['url'],
        owner_id=current_user.id,
        service_type=data.get('service_type', 'api'),
        cost_per_request=data.get('cost_per_request', 0.0001),
        cost_per_gb_hour=data.get('cost_per_gb_hour', 0.10),
        alert_thresholds=data.get('alert_thresholds', {}),
        maintenance_window=data.get('maintenance_window', '')
    )
    
    db.session.add(service)
    db.session.commit()
    
    # Perform initial health check
    check_service_health(service)
    
    REQUEST_COUNT.labels(method='POST', endpoint='/api/services', status=201).inc()
    return jsonify({
        'id': service.id,
        'name': service.name,
        'url': service.url,
        'status': service.status
    }), 201

@app.route('/api/services/<int:service_id>/metrics', methods=['GET'])
@token_required
def get_service_metrics(current_user, service_id):
    """Get metrics for a specific service with enhanced data"""
    service = Service.query.get_or_404(service_id)
    
    # Get metrics from last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    metrics = Metric.query.filter(
        Metric.service_id == service_id,
        Metric.timestamp >= yesterday
    ).order_by(Metric.timestamp.desc()).all()
    
    REQUEST_COUNT.labels(method='GET', endpoint=f'/api/services/{service_id}/metrics', status=200).inc()
    
    return jsonify([{
        'timestamp': m.timestamp.isoformat(),
        'response_time': m.response_time,
        'status_code': m.status_code,
        'error': m.error,
        'uptime': m.uptime,
        'cost': m.cost,
        'request_size': m.request_size,
        'response_size': m.response_size
    } for m in metrics])

@app.route('/api/services/<int:service_id>/cost-analysis', methods=['GET'])
@token_required
def get_service_cost_analysis(current_user, service_id):
    """Get cost analysis for a specific service"""
    service = Service.query.get_or_404(service_id)
    
    # Get metrics from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    metrics = Metric.query.filter(
        Metric.service_id == service_id,
        Metric.timestamp >= thirty_days_ago
    ).all()
    
    total_cost = sum(m.cost for m in metrics)
    total_requests = len(metrics)
    avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
    
    # Calculate cost trends
    daily_costs = {}
    for metric in metrics:
        date = metric.timestamp.date().isoformat()
        daily_costs[date] = daily_costs.get(date, 0) + metric.cost
    
    return jsonify({
        'service_name': service.name,
        'total_cost_30_days': round(total_cost, 6),
        'total_requests_30_days': total_requests,
        'avg_cost_per_request': round(avg_cost_per_request, 6),
        'daily_costs': daily_costs,
        'cost_per_request': service.cost_per_request,
        'cost_per_gb_hour': service.cost_per_gb_hour
    })

@app.route('/api/incidents', methods=['GET'])
@token_required
def get_incidents(current_user):
    """Get all incidents with enhanced data"""
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    REQUEST_COUNT.labels(method='GET', endpoint='/api/incidents', status=200).inc()
    
    return jsonify([{
        'id': i.id,
        'service_id': i.service_id,
        'title': i.title,
        'description': i.description,
        'severity': i.severity,
        'status': i.status,
        'created_at': i.created_at.isoformat(),
        'resolved_at': i.resolved_at.isoformat() if i.resolved_at else None,
        'assigned_to': i.assigned_to,
        'resolution_notes': i.resolution_notes,
        'sla_target': i.sla_target.isoformat() if i.sla_target else None,
        'actual_resolution_time': i.actual_resolution_time
    } for i in incidents])

@app.route('/api/incidents', methods=['POST'])
@token_required
def create_incident(current_user):
    """Create a new incident with enhanced data"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'service_id' not in data:
        return jsonify({'error': 'Title and service_id are required'}), 400
    
    incident = Incident(
        service_id=data['service_id'],
        title=data['title'],
        description=data.get('description', ''),
        severity=data.get('severity', 'medium'),
        assigned_to=data.get('assigned_to'),
        sla_target=datetime.utcnow() + timedelta(hours=data.get('sla_hours', 4))
    )
    
    db.session.add(incident)
    db.session.commit()
    
    REQUEST_COUNT.labels(method='POST', endpoint='/api/incidents', status=201).inc()
    return jsonify({
        'id': incident.id,
        'title': incident.title,
        'status': incident.status
    }), 201

@app.route('/api/incidents/<int:incident_id>/resolve', methods=['POST'])
@token_required
def resolve_incident(current_user, incident_id):
    """Resolve an incident with enhanced tracking"""
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json()
    
    incident.status = 'resolved'
    incident.resolved_at = datetime.utcnow()
    incident.resolution_notes = data.get('resolution_notes', '')
    
    # Calculate actual resolution time
    if incident.sla_target:
        resolution_time = (incident.resolved_at - incident.created_at).total_seconds() / 3600  # hours
        incident.actual_resolution_time = resolution_time
    
    db.session.commit()
    
    REQUEST_COUNT.labels(method='POST', endpoint=f'/api/incidents/{incident_id}/resolve', status=200).inc()
    return jsonify({'message': 'Incident resolved successfully'})

@app.route('/api/maintenance', methods=['GET'])
@token_required
def get_maintenance_schedules(current_user):
    """Get maintenance schedules"""
    maintenance = Maintenance.query.order_by(Maintenance.start_time.desc()).all()
    
    return jsonify([{
        'id': m.id,
        'service_id': m.service_id,
        'title': m.title,
        'description': m.description,
        'start_time': m.start_time.isoformat(),
        'end_time': m.end_time.isoformat(),
        'status': m.status,
        'type': m.type,
        'impact_level': m.impact_level
    } for m in maintenance])

@app.route('/api/maintenance', methods=['POST'])
@token_required
def create_maintenance_schedule(current_user):
    """Create a maintenance schedule"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'service_id' not in data:
        return jsonify({'error': 'Title and service_id are required'}), 400
    
    maintenance = Maintenance(
        service_id=data['service_id'],
        title=data['title'],
        description=data.get('description', ''),
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        type=data.get('type', 'planned'),
        impact_level=data.get('impact_level', 'low'),
        created_by=current_user.id
    )
    
    db.session.add(maintenance)
    db.session.commit()
    
    return jsonify({
        'id': maintenance.id,
        'title': maintenance.title,
        'status': maintenance.status
    }), 201

@app.route('/api/dashboard/stats')
@token_required
def dashboard_stats(current_user):
    """Get enhanced dashboard statistics"""
    total_services = Service.query.count()
    healthy_services = Service.query.filter_by(status='healthy').count()
    down_services = Service.query.filter_by(status='down').count()
    open_incidents = Incident.query.filter_by(status='open').count()
    
    # Calculate average response time and costs
    recent_metrics = Metric.query.filter(
        Metric.timestamp >= datetime.utcnow() - timedelta(hours=1)
    ).all()
    
    avg_response_time = 0
    total_cost_last_hour = 0
    if recent_metrics:
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        total_cost_last_hour = sum(m.cost for m in recent_metrics)
    
    # SLA compliance
    sla_incidents = Incident.query.filter(
        Incident.sla_target.isnot(None),
        Incident.status == 'resolved'
    ).all()
    
    sla_compliance = 0
    if sla_incidents:
        on_time_resolutions = sum(1 for i in sla_incidents if i.actual_resolution_time and i.actual_resolution_time <= 4)
        sla_compliance = (on_time_resolutions / len(sla_incidents)) * 100
    
    REQUEST_COUNT.labels(method='GET', endpoint='/api/dashboard/stats', status=200).inc()
    
    return jsonify({
        'total_services': total_services,
        'healthy_services': healthy_services,
        'down_services': down_services,
        'open_incidents': open_incidents,
        'avg_response_time': round(avg_response_time, 3),
        'total_cost_last_hour': round(total_cost_last_hour, 6),
        'sla_compliance': round(sla_compliance, 1),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/metrics')
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Error handlers
@app.errorhandler(404)
def not_found(error):
    REQUEST_COUNT.labels(method='GET', endpoint='404', status=404).inc()
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    REQUEST_COUNT.labels(method='GET', endpoint='500', status=500).inc()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    logger.info("Starting Cloud Health Dashboard Phase 2")
    app.run(debug=True, host='0.0.0.0', port=5000)
