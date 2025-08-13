from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import time
import json
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import threading
import schedule

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///health_dashboard.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')
SERVICE_HEALTH = Gauge('service_health_status', 'Service health status', ['service_name'])
ERROR_RATE = Counter('service_errors_total', 'Total service errors', ['service_name'])

# Database Models
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='unknown')
    last_check = db.Column(db.DateTime, default=datetime.utcnow)
    uptime = db.Column(db.Float, default=0.0)
    response_time = db.Column(db.Float, default=0.0)
    error_count = db.Column(db.Integer, default=0)
    total_checks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)
    status_code = db.Column(db.Integer)
    error = db.Column(db.Boolean, default=False)
    uptime = db.Column(db.Float)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    threshold = db.Column(db.Float)
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

# Health check function
def check_service_health(service):
    """Check the health of a specific service"""
    start_time = time.time()
    try:
        response = requests.get(service.url, timeout=10)
        response_time = time.time() - start_time
        status_code = response.status_code
        
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
        
        # Record metric
        metric = Metric(
            service_id=service.id,
            response_time=response_time,
            status_code=status_code,
            error=False,
            uptime=service.uptime
        )
        db.session.add(metric)
        
        # Update Prometheus metrics
        SERVICE_HEALTH.labels(service_name=service.name).set(1 if service.status == 'healthy' else 0)
        
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
            uptime=0.0
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
                status='open'
            )
            db.session.add(incident)
    
    db.session.commit()

# Background health checker
def run_health_checks():
    """Run health checks for all services"""
    with app.app_context():
        services = Service.query.all()
        for service in services:
            check_service_health(service)

def schedule_health_checks():
    """Schedule health checks every 30 seconds"""
    schedule.every(30).seconds.do(run_health_checks)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start health check scheduler in background
health_check_thread = threading.Thread(target=schedule_health_checks, daemon=True)
health_check_thread.start()

# API Routes
@app.route('/api/health')
def health():
    """Overall system health endpoint"""
    REQUEST_COUNT.labels(method='GET', endpoint='/api/health', status=200).inc()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/services', methods=['GET'])
def get_services():
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
        'total_checks': s.total_checks
    } for s in services])

@app.route('/api/services', methods=['POST'])
def add_service():
    """Add a new service to monitor"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'url' not in data:
        return jsonify({'error': 'Name and URL are required'}), 400
    
    service = Service(
        name=data['name'],
        url=data['url']
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

@app.route('/api/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """Get a specific service"""
    service = Service.query.get_or_404(service_id)
    REQUEST_COUNT.labels(method='GET', endpoint=f'/api/services/{service_id}', status=200).inc()
    
    return jsonify({
        'id': service.id,
        'name': service.name,
        'url': service.url,
        'status': service.status,
        'last_check': service.last_check.isoformat() if service.last_check else None,
        'uptime': service.uptime,
        'response_time': service.response_time,
        'error_count': service.error_count,
        'total_checks': service.total_checks
    })

@app.route('/api/services/<int:service_id>/metrics', methods=['GET'])
def get_service_metrics(service_id):
    """Get metrics for a specific service"""
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
        'uptime': m.uptime
    } for m in metrics])

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get all incidents"""
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
        'resolved_at': i.resolved_at.isoformat() if i.resolved_at else None
    } for i in incidents])

@app.route('/api/incidents', methods=['POST'])
def create_incident():
    """Create a new incident"""
    data = request.get_json()
    
    if not data or 'title' not in data or 'service_id' not in data:
        return jsonify({'error': 'Title and service_id are required'}), 400
    
    incident = Incident(
        service_id=data['service_id'],
        title=data['title'],
        description=data.get('description', ''),
        severity=data.get('severity', 'medium')
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
def resolve_incident(incident_id):
    """Resolve an incident"""
    incident = Incident.query.get_or_404(incident_id)
    incident.status = 'resolved'
    incident.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    REQUEST_COUNT.labels(method='POST', endpoint=f'/api/incidents/{incident_id}/resolve', status=200).inc()
    return jsonify({'message': 'Incident resolved successfully'})

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    alerts = Alert.query.order_by(Alert.triggered_at.desc()).all()
    REQUEST_COUNT.labels(method='GET', endpoint='/api/alerts', status=200).inc()
    
    return jsonify([{
        'id': a.id,
        'service_id': a.service_id,
        'type': a.type,
        'message': a.message,
        'threshold': a.threshold,
        'triggered_at': a.triggered_at.isoformat(),
        'resolved_at': a.resolved_at.isoformat() if a.resolved_at else None
    } for a in alerts])

@app.route('/api/metrics')
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get dashboard statistics"""
    total_services = Service.query.count()
    healthy_services = Service.query.filter_by(status='healthy').count()
    down_services = Service.query.filter_by(status='down').count()
    open_incidents = Incident.query.filter_by(status='open').count()
    
    # Calculate average response time
    recent_metrics = Metric.query.filter(
        Metric.timestamp >= datetime.utcnow() - timedelta(hours=1)
    ).all()
    
    avg_response_time = 0
    if recent_metrics:
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
    
    REQUEST_COUNT.labels(method='GET', endpoint='/api/dashboard/stats', status=200).inc()
    
    return jsonify({
        'total_services': total_services,
        'healthy_services': healthy_services,
        'down_services': down_services,
        'open_incidents': open_incidents,
        'avg_response_time': round(avg_response_time, 3),
        'timestamp': datetime.utcnow().isoformat()
    })

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
    
    app.run(debug=True, host='0.0.0.0', port=5000)
