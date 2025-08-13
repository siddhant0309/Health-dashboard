# Cloud Health Dashboard - API Documentation

## Overview

The Cloud Health Dashboard API provides RESTful endpoints for monitoring cloud services, managing incidents, and retrieving performance metrics. The API is built with Flask and follows REST conventions.

## Base URL

- **Development**: `http://localhost:5000/api`
- **Production**: `https://your-domain.com/api`

## Authentication

Currently, the API does not require authentication. For production use, consider implementing JWT authentication.

## Response Format

All API responses are returned in JSON format with the following structure:

```json
{
  "status": "success",
  "data": {...},
  "message": "Optional message"
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes and error messages:

```json
{
  "error": "Error description",
  "status_code": 400
}
```

## Endpoints

### 1. Health Check

#### GET `/api/health`

Returns the overall system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK`: System is healthy

---

### 2. Services

#### GET `/api/services`

Retrieves all monitored services.

**Response:**
```json
[
  {
    "id": 1,
    "name": "User Authentication API",
    "url": "https://api.example.com/health",
    "status": "healthy",
    "last_check": "2024-01-15T10:30:00Z",
    "uptime": 99.8,
    "response_time": 0.245,
    "error_count": 2,
    "total_checks": 150
  }
]
```

**Status Codes:**
- `200 OK`: Services retrieved successfully

---

#### POST `/api/services`

Adds a new service to monitor.

**Request Body:**
```json
{
  "name": "Service Name",
  "url": "https://api.example.com/health"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Service Name",
  "url": "https://api.example.com/health",
  "status": "unknown"
}
```

**Status Codes:**
- `201 Created`: Service created successfully
- `400 Bad Request`: Invalid input data

**Validation:**
- `name`: Required, string, max 100 characters
- `url`: Required, valid URL format

---

#### GET `/api/services/{service_id}`

Retrieves a specific service by ID.

**Parameters:**
- `service_id` (path): Service identifier

**Response:**
```json
{
  "id": 1,
  "name": "User Authentication API",
  "url": "https://api.example.com/health",
  "status": "healthy",
  "last_check": "2024-01-15T10:30:00Z",
  "uptime": 99.8,
  "response_time": 0.245,
  "error_count": 2,
  "total_checks": 150
}
```

**Status Codes:**
- `200 OK`: Service retrieved successfully
- `404 Not Found`: Service not found

---

#### GET `/api/services/{service_id}/metrics`

Retrieves metrics for a specific service.

**Parameters:**
- `service_id` (path): Service identifier

**Query Parameters:**
- `hours` (optional): Number of hours to look back (default: 24)

**Response:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "response_time": 0.245,
    "status_code": 200,
    "error": false,
    "uptime": 100.0
  }
]
```

**Status Codes:**
- `200 OK`: Metrics retrieved successfully
- `404 Not Found`: Service not found

---

### 3. Incidents

#### GET `/api/incidents`

Retrieves all incidents.

**Query Parameters:**
- `status` (optional): Filter by status (`open`, `investigating`, `resolved`)
- `severity` (optional): Filter by severity (`low`, `medium`, `high`, `critical`)
- `service_id` (optional): Filter by service ID

**Response:**
```json
[
  {
    "id": 1,
    "service_id": 1,
    "title": "Service is down",
    "description": "Service is not responding to health checks",
    "severity": "high",
    "status": "open",
    "created_at": "2024-01-15T10:30:00Z",
    "resolved_at": null
  }
]
```

**Status Codes:**
- `200 OK`: Incidents retrieved successfully

---

#### POST `/api/incidents`

Creates a new incident.

**Request Body:**
```json
{
  "service_id": 1,
  "title": "Incident Title",
  "description": "Incident description",
  "severity": "medium"
}
```

**Response:**
```json
{
  "id": 2,
  "title": "Incident Title",
  "status": "open"
}
```

**Status Codes:**
- `201 Created`: Incident created successfully
- `400 Bad Request`: Invalid input data

**Validation:**
- `service_id`: Required, integer, must exist
- `title`: Required, string, max 200 characters
- `description`: Optional, string
- `severity`: Optional, enum (`low`, `medium`, `high`, `critical`), default: `medium`

---

#### POST `/api/incidents/{incident_id}/resolve`

Resolves an incident.

**Parameters:**
- `incident_id` (path): Incident identifier

**Response:**
```json
{
  "message": "Incident resolved successfully"
}
```

**Status Codes:**
- `200 OK`: Incident resolved successfully
- `404 Not Found`: Incident not found

---

### 4. Alerts

#### GET `/api/alerts`

Retrieves all alerts.

**Query Parameters:**
- `type` (optional): Filter by alert type
- `service_id` (optional): Filter by service ID
- `resolved` (optional): Filter by resolution status (`true`/`false`)

**Response:**
```json
[
  {
    "id": 1,
    "service_id": 1,
    "type": "high_response_time",
    "message": "Response time exceeded threshold",
    "threshold": 2.0,
    "triggered_at": "2024-01-15T10:30:00Z",
    "resolved_at": null
  }
]
```

**Status Codes:**
- `200 OK`: Alerts retrieved successfully

---

### 5. Dashboard Statistics

#### GET `/api/dashboard/stats`

Retrieves dashboard overview statistics.

**Response:**
```json
{
  "total_services": 5,
  "healthy_services": 4,
  "down_services": 1,
  "open_incidents": 2,
  "avg_response_time": 0.456,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Statistics retrieved successfully

---

### 6. Prometheus Metrics

#### GET `/api/metrics`

Returns Prometheus-formatted metrics for monitoring the dashboard itself.

**Response:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/health",status="200"} 45

# HELP service_health_status Service health status
# TYPE service_health_status gauge
service_health_status{service_name="User Authentication API"} 1
```

**Status Codes:**
- `200 OK`: Metrics returned successfully
- `Content-Type`: `text/plain; version=0.0.4; charset=utf-8`

---

## Data Models

### Service

```json
{
  "id": "integer",
  "name": "string",
  "url": "string",
  "status": "enum(healthy|degraded|down|unknown)",
  "last_check": "datetime",
  "uptime": "float",
  "response_time": "float",
  "error_count": "integer",
  "total_checks": "integer",
  "created_at": "datetime"
}
```

### Metric

```json
{
  "id": "integer",
  "service_id": "integer",
  "timestamp": "datetime",
  "response_time": "float",
  "status_code": "integer",
  "error": "boolean",
  "uptime": "float"
}
```

### Incident

```json
{
  "id": "integer",
  "service_id": "integer",
  "title": "string",
  "description": "string",
  "severity": "enum(low|medium|high|critical)",
  "status": "enum(open|investigating|resolved)",
  "created_at": "datetime",
  "resolved_at": "datetime|null"
}
```

### Alert

```json
{
  "id": "integer",
  "service_id": "integer",
  "type": "string",
  "message": "string",
  "threshold": "float",
  "triggered_at": "datetime",
  "resolved_at": "datetime|null"
}
```

## Rate Limiting

Currently, the API does not implement rate limiting. For production use, consider implementing rate limiting to prevent abuse.

## CORS

The API supports CORS for cross-origin requests. The default configuration allows requests from `http://localhost:3000`.

## Health Check Endpoints

### External Health Checks

The API provides several endpoints for external monitoring:

- `/api/health` - Overall system health
- `/api/metrics` - Prometheus metrics
- `/api/dashboard/stats` - System statistics

### Monitoring Integration

These endpoints can be integrated with:
- **Prometheus**: Scrape `/api/metrics`
- **Grafana**: Use metrics for dashboards
- **Uptime Monitors**: Check `/api/health`
- **Load Balancers**: Health check `/api/health`

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

## Examples

### cURL Examples

#### Add a new service
```bash
curl -X POST http://localhost:5000/api/services \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Payment API",
    "url": "https://api.payment.com/health"
  }'
```

#### Get service metrics
```bash
curl "http://localhost:5000/api/services/1/metrics?hours=48"
```

#### Resolve an incident
```bash
curl -X POST http://localhost:5000/api/incidents/1/resolve
```

#### Get dashboard statistics
```bash
curl http://localhost:5000/api/dashboard/stats
```

### JavaScript Examples

#### Fetch services
```javascript
const response = await fetch('/api/services');
const services = await response.json();
console.log(services);
```

#### Add service
```javascript
const response = await fetch('/api/services', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'New Service',
    url: 'https://api.example.com/health'
  })
});
const service = await response.json();
```

#### Get metrics
```javascript
const response = await fetch('/api/services/1/metrics?hours=24');
const metrics = await response.json();
console.log(metrics);
```

## Testing

### API Testing Tools

- **Postman**: Import the API endpoints
- **Insomnia**: Test API requests
- **cURL**: Command-line testing
- **Python requests**: Automated testing

### Test Data

The API includes sample data for testing:
- 5 sample services with different health statuses
- Sample incidents and alerts
- Historical metrics data

## Versioning

The current API version is v1.0.0. Future versions will maintain backward compatibility where possible.

## Support

For API support or questions:
1. Check the implementation guide
2. Review the error messages
3. Test with the provided examples
4. Check the application logs

## Future Enhancements

Planned API improvements:
- **Authentication**: JWT token support
- **Rate Limiting**: Request throttling
- **Webhooks**: Real-time notifications
- **GraphQL**: Alternative query interface
- **Bulk Operations**: Batch service management
