# 🌟 Cloud Service Health Dashboard - Phase 2

*A comprehensive B2B-style SaaS observability tool with advanced monitoring, cost analysis, and enterprise features*

## 🚀 What's New in Phase 2

### ✨ Enhanced Features
- **🔐 JWT Authentication & Role-Based Access Control**
- **💰 Advanced Cost Tracking & Optimization**
- **📊 SLA Monitoring & Compliance Tracking**
- **🛠️ Maintenance Scheduling & Management**
- **📈 Enhanced Metrics & Analytics**
- **🔔 Smart Alerting with Thresholds**
- **👥 Multi-User Support & Team Management**

### 🏗️ Architecture Improvements
- **Enhanced Database Models** with relationships and constraints
- **Modular Service Architecture** for better maintainability
- **Comprehensive Logging & Error Handling**
- **Advanced Prometheus Metrics** for observability
- **Cost Analysis Engine** with optimization recommendations

## 🎯 Project Overview

The Cloud Service Health Dashboard is a comprehensive B2B-style SaaS observability tool designed to monitor, track, and manage the health of cloud services. Built as a college project, it demonstrates modern DevOps practices, cloud computing concepts, and full-stack development skills.

### 🌟 Key Features

#### 1. **Service Monitoring**
- **Real-time Health Checks**: Automated monitoring every 30 seconds
- **Status Tracking**: Healthy, degraded, and down status detection
- **Performance Metrics**: Response time, uptime, and error rate monitoring
- **HTTP Health Checks**: Configurable timeout and status code validation

#### 2. **Advanced Cost Management**
- **Per-Request Cost Tracking**: Monitor costs at the request level
- **Data Transfer Cost Analysis**: Track bandwidth and storage costs
- **Cost Optimization Recommendations**: AI-powered suggestions for cost reduction
- **Cost Forecasting**: Predict future costs based on historical data
- **Efficiency Scoring**: Rate services on cost-effectiveness

#### 3. **Enhanced Alerting & Incident Management**
- **Smart Thresholds**: Configurable alert thresholds per service
- **SLA Monitoring**: Track resolution times against targets
- **Incident Assignment**: Assign incidents to team members
- **Resolution Tracking**: Monitor incident resolution progress
- **Escalation Management**: Automatic escalation for critical issues

#### 4. **Maintenance & Operations**
- **Scheduled Maintenance**: Plan and track maintenance windows
- **Impact Assessment**: Evaluate maintenance impact on services
- **Team Coordination**: Coordinate maintenance across teams
- **Downtime Planning**: Minimize service disruption

#### 5. **User Management & Security**
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Admin, Operator, and User roles
- **User Profiles**: Manage user information and preferences
- **Session Management**: Secure session handling

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** with Flask framework
- **SQLAlchemy ORM** with PostgreSQL support
- **JWT Authentication** with bcrypt password hashing
- **Prometheus Metrics** for observability
- **Background Task Scheduling** with threading
- **Comprehensive Logging** and error handling

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for modern UI design
- **React Router** for navigation
- **Axios** for API communication
- **Recharts** for data visualization
- **React Hot Toast** for notifications

### Database & Infrastructure
- **SQLite** (development) / **PostgreSQL** (production)
- **Redis** for caching and session storage
- **Docker** and **Docker Compose** for containerization
- **Nginx** reverse proxy (optional)

## 🚀 Quick Start

### Option 1: Quick Start Scripts
- **Windows**: Double-click `start.bat`
- **Linux/Mac**: Run `./start.sh` (make executable with `chmod +x start.sh`)

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py  # Initialize database with sample data
python app.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Option 3: Docker (Recommended for Production)
```bash
docker-compose up --build
```

## 🔐 Authentication

### Default Users (Phase 2)
The system comes with pre-configured users for testing:

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `password123` | Admin | Full access to all features |
| `operator` | `password123` | Operator | Service management & incident resolution |
| `developer` | `password123` | User | Read-only access to monitoring data |

### API Authentication
All API endpoints (except `/api/auth/*`) require a valid JWT token in the Authorization header:
```bash
Authorization: Bearer <your-jwt-token>
```

## 📊 Dashboard Features

### 1. **Overview Dashboard**
- Service health summary
- Cost overview and trends
- SLA compliance metrics
- Recent incidents and alerts

### 2. **Service Management**
- Add/remove services
- Configure monitoring parameters
- Set cost thresholds
- Define maintenance windows

### 3. **Cost Analysis**
- Per-service cost breakdown
- Cost optimization recommendations
- Cost forecasting and trends
- Efficiency scoring

### 4. **Incident Management**
- Incident creation and tracking
- SLA monitoring and compliance
- Team assignment and collaboration
- Resolution tracking and reporting

### 5. **Maintenance Planning**
- Schedule maintenance windows
- Impact assessment
- Team coordination
- Downtime planning

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///health_dashboard.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Monitoring
HEALTH_CHECK_INTERVAL=30
REQUEST_TIMEOUT=10

# External Services
SLACK_WEBHOOK_URL=your-slack-webhook-url
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-email-password

# Cost Analysis
COST_ALERT_THRESHOLD=0.001
COST_OPTIMIZATION_ENABLED=true
```

### Service Configuration
Each service can be configured with:
- **Alert Thresholds**: Response time, cost, and error rate limits
- **Cost Parameters**: Per-request and per-GB-hour costs
- **Maintenance Windows**: Scheduled maintenance periods
- **Service Type**: API, database, storage, compute, etc.

## 📈 Monitoring Endpoints

### Health Check
- `GET /api/health` - Overall system health

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - User profile
- `POST /api/auth/refresh` - Refresh token

### Services
- `GET /api/services` - List all services
- `POST /api/services` - Add new service
- `GET /api/services/{id}/metrics` - Service metrics
- `GET /api/services/{id}/cost-analysis` - Cost analysis

### Incidents & Alerts
- `GET /api/incidents` - List incidents
- `POST /api/incidents` - Create incident
- `POST /api/incidents/{id}/resolve` - Resolve incident

### Maintenance
- `GET /api/maintenance` - List maintenance schedules
- `POST /api/maintenance` - Schedule maintenance

### Metrics
- `GET /api/metrics` - Prometheus metrics
- `GET /api/dashboard/stats` - Dashboard statistics

## 🚀 Deployment Options

### 1. **Render (Recommended for Students)**
- Free tier available
- Automatic deployments from GitHub
- Built-in PostgreSQL database
- Easy SSL configuration

### 2. **Heroku**
- Free tier available
- Simple deployment process
- Add-on services for databases
- Automatic scaling

### 3. **Docker Deployment**
- Production-ready configuration
- Multi-service architecture
- Easy scaling and management
- Environment isolation

### 4. **Local Development**
- SQLite database for simplicity
- Hot reloading for development
- Easy debugging and testing

## 📚 Documentation

- **[Product Brief](docs/product_brief.md)** - Project overview and requirements
- **[Implementation Guide](docs/implementation_guide.md)** - Setup and deployment instructions
- **[API Documentation](docs/api_docs.md)** - Complete API reference
- **[Release Notes](docs/release_notes.md)** - Version history and changes

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
python -m pytest --cov=app tests/
```

### Frontend Testing
```bash
cd frontend
npm test
npm run build
```

## 🔧 Development

### Code Quality
- **Black** for Python code formatting
- **Flake8** for Python linting
- **ESLint** for JavaScript/TypeScript linting
- **Prettier** for code formatting

### Database Migrations
```bash
cd backend
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is created for educational purposes as part of a college course on Cloud Computing and DevOps.

## 🙏 Acknowledgments

- **Flask** community for the excellent web framework
- **React** team for the powerful frontend library
- **Tailwind CSS** for the utility-first CSS framework
- **Prometheus** for monitoring and metrics standards

---

*Built with ❤️ for learning modern software development practices*

*Phase 2 - Enhanced with enterprise-grade features for production readiness*
