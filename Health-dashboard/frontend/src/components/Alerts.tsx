import React from 'react';
import { useServiceContext } from '../contexts/ServiceContext';
import { 
  Bell, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  MessageSquare,
  Calendar,
  TrendingUp
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';

const Alerts: React.FC = () => {
  const { alerts, services, loading } = useServiceContext();

  const getAlertTypeColor = (type: string) => {
    switch (type) {
      case 'service_down':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high_response_time':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'high_error_rate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low_uptime':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'service_down':
        return <AlertTriangle className="w-5 h-5 text-red-600" />;
      case 'high_response_time':
        return <TrendingUp className="w-5 h-5 text-orange-600" />;
      case 'high_error_rate':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'low_uptime':
        return <TrendingUp className="w-5 h-5 text-purple-600" />;
      default:
        return <Bell className="w-5 h-5 text-gray-600" />;
    }
  };

  const getServiceName = (serviceId: number) => {
    const service = services.find(s => s.id === serviceId);
    return service ? service.name : 'Unknown Service';
  };

  const formatAlertType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-1">System alerts and notifications</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm text-gray-600">Active Alerts</p>
            <p className="text-2xl font-bold text-orange-600">
              {alerts.filter(a => !a.resolved_at).length}
            </p>
          </div>
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No alerts triggered</h3>
            <p className="text-gray-600">All systems are operating within normal parameters</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`bg-white rounded-lg shadow-sm border-2 p-6 ${
                alert.resolved_at ? 'border-gray-200 opacity-75' : 'border-orange-200'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getAlertIcon(alert.type)}
                    <h3 className="text-lg font-semibold text-gray-900">
                      {formatAlertType(alert.type)}
                    </h3>
                  </div>
                  <p className="text-gray-600 mb-3">{alert.message}</p>
                  
                  {/* Service and Threshold Info */}
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-4 h-4" />
                      {getServiceName(alert.service_id)}
                    </span>
                    {alert.threshold && (
                      <span className="flex items-center gap-1">
                        <TrendingUp className="w-4 h-4" />
                        Threshold: {alert.threshold}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {format(new Date(alert.triggered_at), 'MMM dd, yyyy HH:mm')}
                    </span>
                  </div>
                </div>
                
                {/* Alert Type Badge */}
                <div className="ml-4">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getAlertTypeColor(alert.type)}`}>
                    {formatAlertType(alert.type)}
                  </span>
                </div>
              </div>

              {/* Status and Timeline */}
              <div className="border-t border-gray-100 pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>
                      Triggered {formatDistanceToNow(new Date(alert.triggered_at))} ago
                    </span>
                  </div>
                  
                  {alert.resolved_at ? (
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <CheckCircle className="w-4 h-4" />
                      <span>
                        Resolved {formatDistanceToNow(new Date(alert.resolved_at))} ago
                      </span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-sm text-orange-600">
                      <AlertTriangle className="w-4 h-4" />
                      <span>Active</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading alerts...</p>
        </div>
      )}
    </div>
  );
};

export default Alerts;
