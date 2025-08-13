import React from 'react';
import { useServiceContext } from '../contexts/ServiceContext';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Server, 
  TrendingUp,
  XCircle,
  RefreshCw
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const { 
    services, 
    incidents, 
    alerts, 
    stats, 
    loading, 
    error, 
    refreshData 
  } = useServiceContext();

  const handleRefresh = async () => {
    try {
      await refreshData();
      toast.success('Dashboard refreshed successfully');
    } catch (err) {
      toast.error('Failed to refresh dashboard');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-success-600 bg-success-50 border-success-200';
      case 'degraded':
        return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'down':
        return 'text-danger-600 bg-danger-50 border-danger-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-warning-600" />;
      case 'down':
        return <XCircle className="w-5 h-5 text-danger-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-primary-600" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <XCircle className="w-8 h-8 mx-auto mb-4 text-danger-600" />
          <p className="text-danger-600 mb-2">Error loading dashboard</p>
          <p className="text-gray-600 text-sm">{error}</p>
          <button 
            onClick={handleRefresh}
            className="mt-4 btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Cloud Service Health Overview
            {stats?.timestamp && (
              <span className="ml-2 text-sm text-gray-500">
                Last updated: {formatDistanceToNow(new Date(stats.timestamp))} ago
              </span>
            )}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="btn-primary flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Server className="w-6 h-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Services</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_services}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-success-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-success-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Healthy Services</p>
                <p className="text-2xl font-bold text-success-600">{stats.healthy_services}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-danger-100 rounded-lg">
                <XCircle className="w-6 h-6 text-danger-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Down Services</p>
                <p className="text-2xl font-bold text-danger-600">{stats.down_services}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className="p-2 bg-warning-100 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-warning-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Open Incidents</p>
                <p className="text-2xl font-bold text-warning-600">{stats.open_incidents}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      {stats && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Overview</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Average Response Time</span>
                <span className="font-semibold text-gray-900">
                  {stats.avg_response_time.toFixed(3)}s
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ 
                    width: `${Math.min((stats.avg_response_time / 2) * 100, 100)}%` 
                  }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">
                Target: &lt; 2.0s
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Overall Uptime</span>
                <span className="font-semibold text-gray-900">
                  {stats.total_services > 0 
                    ? ((stats.healthy_services / stats.total_services) * 100).toFixed(1)
                    : 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-success-600 h-2 rounded-full transition-all duration-300"
                  style={{ 
                    width: `${stats.total_services > 0 
                      ? (stats.healthy_services / stats.total_services) * 100 
                      : 0}%` 
                  }}
                ></div>
              </div>
              <p className="text-xs text-gray-500">
                Target: &gt; 99.0%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Service Status */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Service Status</h3>
        </div>
        <div className="p-6">
          {services.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No services configured</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {services.map((service) => (
                <div 
                  key={service.id}
                  className={`p-4 rounded-lg border-2 transition-all duration-200 hover:shadow-md ${getStatusColor(service.status)}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 mb-1">{service.name}</h4>
                      <p className="text-sm text-gray-600 mb-2 truncate">{service.url}</p>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="flex items-center gap-1">
                          <Activity className="w-4 h-4" />
                          {service.response_time.toFixed(3)}s
                        </span>
                        <span className="flex items-center gap-1">
                          <TrendingUp className="w-4 h-4" />
                          {service.uptime.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      {getStatusIcon(service.status)}
                    </div>
                  </div>
                  <div className="mt-3 text-xs text-gray-500">
                    Last check: {formatDistanceToNow(new Date(service.last_check))} ago
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recent Incidents */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Incidents</h3>
        </div>
        <div className="p-6">
          {incidents.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No incidents reported</p>
          ) : (
            <div className="space-y-4">
              {incidents.slice(0, 5).map((incident) => (
                <div 
                  key={incident.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{incident.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{incident.description}</p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        incident.severity === 'high' ? 'bg-danger-100 text-danger-800' :
                        incident.severity === 'medium' ? 'bg-warning-100 text-warning-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {incident.severity}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        incident.status === 'open' ? 'bg-blue-100 text-blue-800' :
                        incident.status === 'investigating' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-success-100 text-success-800'
                      }`}>
                        {incident.status}
                      </span>
                    </div>
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    {formatDistanceToNow(new Date(incident.created_at))} ago
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
