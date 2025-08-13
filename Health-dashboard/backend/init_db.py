#!/usr/bin/env python3
"""
Database initialization script for Cloud Health Dashboard
Creates tables and adds sample data for demonstration
"""

from app import app, db, Service, Metric, Incident, Alert
from datetime import datetime, timedelta
import random

def init_database():
    """Initialize the database with tables and sample data"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Add sample services
        print("Adding sample services...")
        sample_services = [
            {
                'name': 'User Authentication API',
                'url': 'https://httpstat.us/200',
                'status': 'healthy'
            },
            {
                'name': 'Payment Processing Service',
                'url': 'https://httpstat.us/200',
                'status': 'healthy'
            },
            {
                'name': 'Database Service',
                'url': 'https://httpstat.us/200',
                'status': 'healthy'
            },
            {
                'name': 'File Storage Service',
                'url': 'https://httpstat.us/500',
                'status': 'degraded'
            },
            {
                'name': 'Email Service',
                'url': 'https://httpstat.us/503',
                'status': 'down'
            }
        ]
        
        services = []
        for service_data in sample_services:
            service = Service(**service_data)
            db.session.add(service)
            services.append(service)
        
        db.session.commit()
        print(f"Added {len(services)} sample services")
        
        # Add sample metrics for the last 24 hours
        print("Adding sample metrics...")
        now = datetime.utcnow()
        for service in services:
            # Generate metrics for the last 24 hours
            for i in range(24):
                timestamp = now - timedelta(hours=i)
                
                # Simulate realistic response times
                if service.status == 'healthy':
                    response_time = random.uniform(0.1, 0.5)
                    status_code = 200
                    error = False
                    uptime = 100.0
                elif service.status == 'degraded':
                    response_time = random.uniform(0.5, 2.0)
                    status_code = random.choice([200, 500, 502])
                    error = status_code != 200
                    uptime = 75.0
                else:  # down
                    response_time = random.uniform(2.0, 10.0)
                    status_code = 0
                    error = True
                    uptime = 0.0
                
                metric = Metric(
                    service_id=service.id,
                    timestamp=timestamp,
                    response_time=response_time,
                    status_code=status_code,
                    error=error,
                    uptime=uptime
                )
                db.session.add(metric)
        
        db.session.commit()
        print("Added sample metrics")
        
        # Add sample incidents
        print("Adding sample incidents...")
        sample_incidents = [
            {
                'service_id': 4,  # File Storage Service
                'title': 'File upload failures',
                'description': 'Users are experiencing intermittent file upload failures. Response times are elevated.',
                'severity': 'medium',
                'status': 'open'
            },
            {
                'service_id': 5,  # Email Service
                'title': 'Email service completely down',
                'description': 'Email service is not responding to any requests. All email functionality is affected.',
                'severity': 'high',
                'status': 'open'
            }
        ]
        
        for incident_data in sample_incidents:
            incident = Incident(**incident_data)
            db.session.add(incident)
        
        db.session.commit()
        print("Added sample incidents")
        
        # Add sample alerts
        print("Adding sample alerts...")
        sample_alerts = [
            {
                'service_id': 4,
                'type': 'high_response_time',
                'message': 'Response time exceeded 2 seconds threshold',
                'threshold': 2.0
            },
            {
                'service_id': 5,
                'type': 'service_down',
                'message': 'Service is not responding',
                'threshold': 0.0
            }
        ]
        
        for alert_data in sample_alerts:
            alert = Alert(**alert_data)
            db.session.add(alert)
        
        db.session.commit()
        print("Added sample alerts")
        
        print("\nDatabase initialization completed successfully!")
        print(f"Total services: {Service.query.count()}")
        print(f"Total metrics: {Metric.query.count()}")
        print(f"Total incidents: {Incident.query.count()}")
        print(f"Total alerts: {Alert.query.count()}")

if __name__ == '__main__':
    init_database()
