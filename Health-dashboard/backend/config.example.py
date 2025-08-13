"""
Configuration file for Cloud Health Dashboard
Copy this file to config.py and update the values as needed
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///health_dashboard.db')
    
    # Monitoring Configuration
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))  # seconds
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))  # seconds
    
    # Alert Configuration
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    
    # Alert Thresholds
    RESPONSE_TIME_THRESHOLD = float(os.getenv('RESPONSE_TIME_THRESHOLD', '2.0'))  # seconds
    ERROR_RATE_THRESHOLD = float(os.getenv('ERROR_RATE_THRESHOLD', '5.0'))  # percentage
    UPTIME_THRESHOLD = float(os.getenv('UPTIME_THRESHOLD', '99.0'))  # percentage
    
    # Prometheus Configuration
    ENABLE_PROMETHEUS = os.getenv('ENABLE_PROMETHEUS', 'True').lower() == 'true'
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '9090'))
    
    # Redis Configuration (for Celery tasks)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Cost Estimation Configuration
    COST_PER_REQUEST = float(os.getenv('COST_PER_REQUEST', '0.0001'))  # dollars per request
    COST_PER_GB_HOUR = float(os.getenv('COST_PER_GB_HOUR', '0.10'))  # dollars per GB-hour
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'health_dashboard.log')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Security Configuration
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))  # seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_URL = 'sqlite:///health_dashboard_dev.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Production security settings
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///health_dashboard_test.db'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    config_name = os.getenv('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])
