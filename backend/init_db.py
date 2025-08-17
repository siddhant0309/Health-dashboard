#!/usr/bin/env python3
"""
Enhanced Database initialization script for Cloud Health Dashboard Phase 2
Creates tables and adds sample data for demonstration
"""

from app import app, db, Service, Metric, Incident, Alert, User, Maintenance
from datetime import datetime, timedelta
import random
import hashlib
import bcrypt

def init_database():
    """Initialize the database with tables and enhanced sample data"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Creating sample users...")
        # Create sample users
        users = []
        sample_users = [
            {'username': 'admin', 'email': 'admin@cloudhealth.com', 'role': 'admin'},
            {'username': 'operator', 'email': 'operator@cloudhealth.com', 'role': 'operator'},
            {'username': 'developer', 'email': 'dev@cloudhealth.com', 'role': 'user'}
        ]
        
        for user_data in sample_users:
            password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt())
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password_hash.decode('utf-8'),
                role=user_data['role']
            )
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        admin_user = users[0]
        
        print("Adding enhanced sample services...")
        sample_services = [
            {
                'name': 'User Authentication API',
                'url': 'https://httpstat.us/200',
                'status': 'healthy',
                'service_type': 'api',
                'cost_per_request': 0.0001,
                'cost_per_gb_hour': 0.15,
                'alert_thresholds': {'response_time': 2.0, 'cost': 0.001, 'error_rate': 5.0},
                'maintenance_window': 'Sun 2:00-4:00 UTC'
            },
            {
                'name': 'Payment Processing Service',
                'url': 'https://httpstat.us/200',
                'status': 'healthy',
                'service_type': 'api',
                'cost_per_request': 0.0005,
                'cost_per_gb_hour': 0.20,
                'alert_thresholds': {'response_time': 3.0, 'cost': 0.002, 'error_rate': 2.0},
                'maintenance_window': 'Mon 1:00-3:00 UTC'
            },
            {
                'name': 'Database Service',
                'url': 'https://httpstat.us/200',
                'status': 'healthy',
                'service_type': 'database',
                'cost_per_request': 0.0002,
                'cost_per_gb_hour': 0.25,
                'alert_thresholds': {'response_time': 1.5, 'cost': 0.001, 'error_rate': 1.0},
                'maintenance_window': 'Sat 3:00-5:00 UTC'
            },
            {
                'name': 'File Storage Service',
                'url': 'https://httpstat.us/500',
                'status': 'degraded',
                'service_type': 'storage',
                'cost_per_request': 0.0003,
                'cost_per_gb_hour': 0.10,
                'alert_thresholds': {'response_time': 5.0, 'cost': 0.003, 'error_rate': 10.0},
                'maintenance_window': 'Fri 4:00-6:00 UTC'
            },
            {
                'name': 'Email Service',
                'url': 'https://httpstat.us/503',
                'status': 'down',
                'service_type': 'api',
                'cost_per_request': 0.0001,
                'cost_per_gb_hour': 0.12,
                'alert_thresholds': {'response_time': 4.0, 'cost': 0.001, 'error_rate': 15.0},
                'maintenance_window': 'Thu 2:00-4:00 UTC'
            },
            {
                'name': 'Analytics Engine',
                'url': 'https://httpstat.us/200',
                'status': 'healthy',
                'service_type': 'compute',
                'cost_per_request': 0.0010,
                'cost_per_gb_hour': 0.30,
                'alert_thresholds': {'response_time': 10.0, 'cost': 0.005, 'error_rate': 3.0},
                'maintenance_window': 'Wed 1:00-3:00 UTC'
            }
        ]
        
        services = []
        for service_data in sample_services:
            service = Service(
                name=service_data['name'],
                url=service_data['url'],
                status=service_data['status'],
                owner_id=admin_user.id,
                service_type=service_data['service_type'],
                cost_per_request=service_data['cost_per_request'],
                cost_per_gb_hour=service_data['cost_per_gb_hour'],
                alert_thresholds=service_data['alert_thresholds'],
                maintenance_window=service_data['maintenance_window']
            )
            services.append(service)
            db.session.add(service)
        
        db.session.commit()
        
        print("Generating enhanced metrics...")
        # Generate metrics for the last 7 days
        for service in services:
            for i in range(168):  # 7 days * 24 hours
                timestamp = datetime.utcnow() - timedelta(hours=i)
                
                # Simulate realistic response times and costs
                if service.status == 'healthy':
                    response_time = random.uniform(0.1, 1.5)
                    status_code = 200
                    error = False
                    uptime = 100.0
                elif service.status == 'degraded':
                    response_time = random.uniform(1.5, 4.0)
                    status_code = random.choice([200, 500, 502])
                    error = status_code != 200
                    uptime = random.uniform(50.0, 90.0)
                else:  # down
                    response_time = random.uniform(5.0, 10.0)
                    status_code = 0
                    error = True
                    uptime = 0.0
                
                # Calculate cost based on service configuration
                cost = service.cost_per_request + (random.randint(100, 1000) / (1024**3)) * service.cost_per_gb_hour
                
                metric = Metric(
                    service_id=service.id,
                    timestamp=timestamp,
                    response_time=response_time,
                    status_code=status_code,
                    error=error,
                    uptime=uptime,
                    cost=cost,
                    request_size=random.randint(50, 500),
                    response_size=random.randint(100, 2000)
                )
                db.session.add(metric)
        
        print("Adding enhanced incidents...")
        # Create incidents with SLA tracking
        incident_data = [
            {
                'service_id': services[3].id,  # File Storage Service
                'title': 'High response time detected',
                'description': 'File Storage Service is responding slowly, affecting user experience',
                'severity': 'medium',
                'assigned_to': users[1].id,  # operator
                'sla_target': datetime.utcnow() + timedelta(hours=2)
            },
            {
                'service_id': services[4].id,  # Email Service
                'title': 'Service completely down',
                'description': 'Email Service is not responding to any requests',
                'severity': 'high',
                'assigned_to': users[0].id,  # admin
                'sla_target': datetime.utcnow() + timedelta(hours=1)
            }
        ]
        
        for incident_info in incident_data:
            incident = Incident(
                service_id=incident_info['service_id'],
                title=incident_info['title'],
                description=incident_info['description'],
                severity=incident_info['severity'],
                assigned_to=incident_info['assigned_to'],
                sla_target=incident_info['sla_target']
            )
            db.session.add(incident)
        
        print("Adding enhanced alerts...")
        # Create alerts with different types
        alert_data = [
            {
                'service_id': services[3].id,
                'type': 'high_response_time',
                'message': 'Response time 3.2s exceeded threshold 2.0s',
                'threshold': 2.0,
                'severity': 'medium'
            },
            {
                'service_id': services[4].id,
                'type': 'service_down',
                'message': 'Service is not responding to health checks',
                'threshold': None,
                'severity': 'high'
            },
            {
                'service_id': services[2].id,
                'type': 'high_cost',
                'message': 'Cost $0.0015 exceeded threshold $0.0010',
                'threshold': 0.0010,
                'severity': 'high'
            }
        ]
        
        for alert_info in alert_data:
            alert = Alert(
                service_id=alert_info['service_id'],
                type=alert_info['type'],
                message=alert_info['message'],
                threshold=alert_info['threshold'],
                severity=alert_info['severity']
            )
            db.session.add(alert)
        
        print("Adding maintenance schedules...")
        # Create maintenance schedules
        maintenance_data = [
            {
                'service_id': services[0].id,  # User Authentication API
                'title': 'Database migration',
                'description': 'Upgrading authentication database to latest version',
                'start_time': datetime.utcnow() + timedelta(days=7),
                'end_time': datetime.utcnow() + timedelta(days=7, hours=2),
                'type': 'planned',
                'impact_level': 'medium'
            },
            {
                'service_id': services[1].id,  # Payment Processing Service
                'title': 'Security patch deployment',
                'description': 'Applying critical security updates to payment processing',
                'start_time': datetime.utcnow() + timedelta(days=3),
                'end_time': datetime.utcnow() + timedelta(days=3, hours=1),
                'type': 'planned',
                'impact_level': 'high'
            }
        ]
        
        for maintenance_info in maintenance_data:
            maintenance = Maintenance(
                service_id=maintenance_info['service_id'],
                title=maintenance_info['title'],
                description=maintenance_info['description'],
                start_time=maintenance_info['start_time'],
                end_time=maintenance_info['end_time'],
                type=maintenance_info['type'],
                impact_level=maintenance_info['impact_level'],
                created_by=admin_user.id
            )
            db.session.add(maintenance)
        
        db.session.commit()
        
        print("Database initialization completed successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(services)} services")
        print("Generated metrics for the last 7 days")
        print("Created sample incidents with SLA tracking")
        print("Created sample alerts with different types")
        print("Created maintenance schedules")
        print("\nDefault login credentials:")
        print("Username: admin, Password: password123")
        print("Username: operator, Password: password123")
        print("Username: developer, Password: password123")

if __name__ == '__main__':
    init_database()
