# Cloud Service Health Dashboard

A comprehensive B2B-style SaaS observability tool designed for monitoring cloud services, built as a college project to demonstrate modern DevOps practices and cloud computing concepts.

## 🚀 Features

- **Real-time Monitoring**: Track latency, error rates, and uptime for cloud services
- **Interactive Dashboard**: Beautiful React-based dashboard with real-time metrics
- **Alert System**: Email and Slack notifications for incidents
- **Cost Estimation**: Usage-based cost calculator for cloud services
- **Incident Management**: Track and manage service incidents
- **Performance Analytics**: P50/P95 latency tracking and trend analysis

## 🏗️ Architecture

- **Backend**: Flask API with monitoring endpoints
- **Frontend**: React dashboard with real-time updates
- **Database**: SQLite for development, PostgreSQL ready for production
- **Monitoring**: Custom health check pipeline
- **Deployment**: Ready for Render/Heroku deployment

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: React, TypeScript, Tailwind CSS
- **Database**: SQLite, PostgreSQL
- **Monitoring**: Custom health checks, Prometheus-style metrics
- **Deployment**: Docker, Render/Heroku ready

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- Basic knowledge of cloud services and APIs

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

## 📊 Dashboard Features

- **Service Overview**: Real-time health status of all monitored services
- **Performance Metrics**: Latency charts, error rate trends, uptime statistics
- **Incident Timeline**: Historical view of service incidents and resolutions
- **Cost Analysis**: Usage-based cost estimation and optimization suggestions
- **Alert Configuration**: Customizable alert thresholds and notification channels

## 🔧 Configuration

Copy `config.example.py` to `config.py` and update:
- Database connection strings
- Alert webhook URLs (Slack, email)
- Service endpoints to monitor
- Alert thresholds

## 📈 Monitoring Endpoints

The backend provides these key endpoints:
- `GET /api/health` - Overall system health
- `GET /api/services` - List all monitored services
- `GET /api/metrics/:service_id` - Service-specific metrics
- `POST /api/incidents` - Report new incidents
- `GET /api/alerts` - Alert history and configuration

## 🚀 Deployment

### Render Deployment
1. Connect your GitHub repository
2. Set environment variables
3. Deploy backend and frontend separately

### Heroku Deployment
1. Install Heroku CLI
2. Create apps for backend and frontend
3. Deploy using Git push

## 📚 Documentation

- [Product Brief](./docs/product_brief.md)
- [Implementation Guide](./docs/implementation_guide.md)
- [API Documentation](./docs/api_docs.md)
- [Release Notes](./docs/release_notes.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is created for educational purposes as part of a college course.

## 👨‍🎓 Project Team

- **Role**: Full-stack developer and DevOps engineer
- **Responsibilities**: Backend API, monitoring pipeline, deployment
- **Skills Demonstrated**: Cloud computing, DevOps, SaaS development, technical writing

---

*Built with ❤️ for learning modern software development practices*
