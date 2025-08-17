"""
Enhanced Configuration file for Cloud Health Dashboard Phase 2
Copy this file to config.py and update the values as needed
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    # Basic Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///health_dashboard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Monitoring Configuration
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))  # seconds
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))  # seconds
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    # Alert Configuration
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
    EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'alerts@cloudhealth.com')
    
    # Prometheus Metrics Configuration
    PROMETHEUS_ENABLED = os.getenv('PROMETHEUS_ENABLED', 'True').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() == 'true'
    
    # Celery Configuration (for background tasks)
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    CELERY_ENABLED = os.getenv('CELERY_ENABLED', 'False').lower() == 'true'
    
    # Cost Analysis Configuration
    COST_ALERT_THRESHOLD = float(os.getenv('COST_ALERT_THRESHOLD', '0.001'))
    COST_OPTIMIZATION_ENABLED = os.getenv('COST_OPTIMIZATION_ENABLED', 'True').lower() == 'true'
    COST_FORECAST_DAYS = int(os.getenv('COST_FORECAST_DAYS', '30'))
    
    # SLA Configuration
    DEFAULT_SLA_HOURS = int(os.getenv('DEFAULT_SLA_HOURS', '4'))
    SLA_ESCALATION_ENABLED = os.getenv('SLA_ESCALATION_ENABLED', 'True').lower() == 'true'
    
    # Security Configuration
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '86400'))  # 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '604800'))  # 7 days
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    LOGIN_LOCKOUT_DURATION = int(os.getenv('LOGIN_LOCKOUT_DURATION', '300'))  # 5 minutes
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'health_dashboard.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per minute')
    RATE_LIMIT_STORAGE_URL = os.getenv('RATE_LIMIT_STORAGE_URL', 'memory://')
    
    # Maintenance Configuration
    MAINTENANCE_MODE_ENABLED = os.getenv('MAINTENANCE_MODE_ENABLED', 'False').lower() == 'true'
    MAINTENANCE_MESSAGE = os.getenv('MAINTENANCE_MESSAGE', 'System is under maintenance')
    
    # Backup Configuration
    BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'False').lower() == 'true'
    BACKUP_SCHEDULE = os.getenv('BACKUP_SCHEDULE', '0 2 * * *')  # Daily at 2 AM
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '100'))
    REQUEST_TIMEOUT_LIMIT = int(os.getenv('REQUEST_TIMEOUT_LIMIT', '30'))
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))  # 5 minutes
    
    # Notification Configuration
    NOTIFICATION_CHANNELS = os.getenv('NOTIFICATION_CHANNELS', 'email,slack').split(',')
    NOTIFICATION_RETRY_ATTEMPTS = int(os.getenv('NOTIFICATION_RETRY_ATTEMPTS', '3'))
    NOTIFICATION_RETRY_DELAY = int(os.getenv('NOTIFICATION_RETRY_DELAY', '60'))  # 1 minute

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_URL = os.getenv('DEV_DATABASE_URL', 'sqlite:///health_dashboard_dev.db')
    LOG_LEVEL = 'DEBUG'
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_URL = os.getenv('DATABASE_URL')
    LOG_LEVEL = 'WARNING'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    
    # Production security settings
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    PASSWORD_MIN_LENGTH = 12
    MAX_LOGIN_ATTEMPTS = 3
    RATE_LIMIT_ENABLED = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'ERROR'

class StagingConfig(Config):
    """Staging configuration"""
    DEBUG = True
    DATABASE_URL = os.getenv('STAGING_DATABASE_URL')
    LOG_LEVEL = 'INFO'
    CORS_ORIGINS = os.getenv('STAGING_CORS_ORIGINS', '').split(',')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Environment-specific overrides
if os.getenv('FLASK_ENV') == 'production':
    # Ensure production security
    Config.SECRET_KEY = os.getenv('SECRET_KEY')
    Config.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    
    if not Config.SECRET_KEY or Config.SECRET_KEY == 'dev-secret-key-change-in-production':
        raise ValueError('SECRET_KEY must be set in production')
    
    if not Config.JWT_SECRET_KEY or Config.JWT_SECRET_KEY == 'jwt-secret-key-change-in-production':
        raise ValueError('JWT_SECRET_KEY must be set in production')
