# Cloud Service Health Dashboard - Implementation Guide

## Overview

This guide provides step-by-step instructions for setting up, running, and deploying the Cloud Service Health Dashboard. The project consists of a Flask backend API and a React frontend dashboard.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Git**: Latest version
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space

### Software Installation

#### 1. Python Installation
```bash
# Windows: Download from python.org
# macOS: brew install python
# Linux: sudo apt-get install python3 python3-pip

# Verify installation
python --version  # or python3 --version
pip --version     # or pip3 --version
```

#### 2. Node.js Installation
```bash
# Windows: Download from nodejs.org
# macOS: brew install node
# Linux: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -

# Verify installation
node --version
npm --version
```

#### 3. Git Installation
```bash
# Windows: Download from git-scm.com
# macOS: brew install git
# Linux: sudo apt-get install git

# Verify installation
git --version
```

## Project Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cloud-health-dashboard
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Copy configuration template
cp config.example.py config.py

# Edit config.py with your settings
# Key configurations:
# - DATABASE_URL: Database connection string
# - SECRET_KEY: Flask secret key
# - SLACK_WEBHOOK_URL: Slack notifications (optional)
# - EMAIL_*: Email alert settings (optional)
```

#### Database Initialization
```bash
python init_db.py
```

#### Run Backend Server
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd ../frontend
npm install
```

#### Environment Configuration
```bash
# Create .env file (optional)
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env
```

#### Run Development Server
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
cloud-health-dashboard/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── init_db.py            # Database initialization
│   ├── requirements.txt      # Python dependencies
│   ├── config.example.py    # Configuration template
│   └── health_dashboard.db  # SQLite database (created)
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── contexts/         # React contexts
│   │   ├── App.tsx          # Main app component
│   │   └── index.tsx        # Entry point
│   ├── package.json         # Node.js dependencies
│   └── tailwind.config.js   # Tailwind CSS configuration
├── docs/                    # Documentation
└── README.md               # Project overview
```

## Configuration

### Backend Configuration

#### Database Configuration
```python
# config.py
DATABASE_URL = 'sqlite:///health_dashboard.db'  # Development
# DATABASE_URL = 'postgresql://user:pass@localhost/db'  # Production
```

#### Monitoring Configuration
```python
HEALTH_CHECK_INTERVAL = 30  # seconds
REQUEST_TIMEOUT = 10        # seconds
RESPONSE_TIME_THRESHOLD = 2.0  # seconds
ERROR_RATE_THRESHOLD = 5.0     # percentage
UPTIME_THRESHOLD = 99.0        # percentage
```

#### Alert Configuration
```python
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/...'
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587
EMAIL_USERNAME = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-app-password'
```

### Frontend Configuration

#### API Configuration
```javascript
// .env
REACT_APP_API_URL=http://localhost:5000/api
```

#### Tailwind CSS Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: { /* custom colors */ },
        success: { /* custom colors */ },
        warning: { /* custom colors */ },
        danger: { /* custom colors */ }
      }
    }
  }
}
```

## Usage

### 1. Adding Services

#### Via Frontend
1. Navigate to Services page
2. Click "Add Service"
3. Enter service name and URL
4. Click "Add Service"

#### Via API
```bash
curl -X POST http://localhost:5000/api/services \
  -H "Content-Type: application/json" \
  -d '{"name": "Test API", "url": "https://httpstat.us/200"}'
```

### 2. Monitoring Services

- Services are automatically monitored every 30 seconds
- Health checks include response time, status code, and error detection
- Metrics are stored in the database for historical analysis

### 3. Viewing Dashboard

- **Overview**: Real-time service status and key metrics
- **Services**: Detailed service information and management
- **Incidents**: Track and resolve service issues
- **Alerts**: View system alerts and notifications
- **Metrics**: Detailed performance analytics

### 4. Managing Incidents

- Incidents are automatically created for service failures
- Manual incident creation for planned maintenance
- Resolution tracking and timeline
- Severity classification and status updates

## Development

### Backend Development

#### Adding New Endpoints
```python
@app.route('/api/new-endpoint', methods=['GET'])
def new_endpoint():
    return jsonify({'message': 'New endpoint'})
```

#### Database Models
```python
class NewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Health Checks
```python
def custom_health_check(service):
    # Custom health check logic
    pass
```

### Frontend Development

#### Adding New Components
```typescript
// src/components/NewComponent.tsx
import React from 'react';

const NewComponent: React.FC = () => {
  return <div>New Component</div>;
};

export default NewComponent;
```

#### Adding New Routes
```typescript
// src/App.tsx
<Route path="/new-route" element={<NewComponent />} />
```

#### Styling with Tailwind
```typescript
<div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  {/* Component content */}
</div>
```

## Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test services endpoint
curl http://localhost:5000/api/services

# Test metrics endpoint
curl http://localhost:5000/api/metrics
```

## Deployment

### 1. Render Deployment

#### Backend Deployment
1. Connect GitHub repository to Render
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Set environment variables

#### Frontend Deployment
1. Create new Static Site
2. Set build command: `npm run build`
3. Set publish directory: `build`

### 2. Heroku Deployment

#### Backend Deployment
```bash
# Install Heroku CLI
heroku create your-app-name
git push heroku main

# Set environment variables
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=your-secret-key
```

#### Frontend Deployment
```bash
# Build and deploy
npm run build
git add build
git commit -m "Add build files"
git push heroku main
```

### 3. Docker Deployment

#### Create Dockerfile
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://...
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## Troubleshooting

### Common Issues

#### Backend Issues
1. **Port already in use**: Change port in `app.py`
2. **Database errors**: Run `python init_db.py`
3. **Import errors**: Check virtual environment activation

#### Frontend Issues
1. **Build errors**: Clear `node_modules` and reinstall
2. **API connection**: Check backend server and CORS settings
3. **Styling issues**: Verify Tailwind CSS configuration

#### Database Issues
1. **Connection errors**: Check database URL and credentials
2. **Migration errors**: Drop and recreate database
3. **Performance issues**: Add database indexes

### Debug Mode

#### Backend Debug
```python
# app.py
app.run(debug=True, host='0.0.0.0', port=5000)
```

#### Frontend Debug
```bash
# Enable React DevTools
npm install -g react-devtools
react-devtools
```

## Performance Optimization

### Backend Optimization
1. **Database indexing** on frequently queried fields
2. **Connection pooling** for database connections
3. **Caching** for static data
4. **Async processing** for health checks

### Frontend Optimization
1. **Code splitting** for large components
2. **Lazy loading** for routes
3. **Memoization** for expensive calculations
4. **Bundle optimization** with webpack

## Security Considerations

### Current Security Features
- CORS configuration
- Input validation
- SQL injection prevention (SQLAlchemy)

### Recommended Enhancements
1. **Authentication**: JWT tokens
2. **Authorization**: Role-based access control
3. **Rate limiting**: API request throttling
4. **HTTPS**: SSL/TLS encryption
5. **Input sanitization**: XSS prevention

## Monitoring and Logging

### Application Monitoring
- Prometheus metrics endpoint: `/api/metrics`
- Health check endpoint: `/api/health`
- Performance monitoring with built-in metrics

### Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Application started")
```

## Conclusion

This implementation guide provides comprehensive instructions for setting up and running the Cloud Service Health Dashboard. The project demonstrates modern software development practices and can serve as a foundation for learning cloud monitoring and DevOps concepts.

For additional support or questions, refer to the project documentation or create an issue in the repository.
