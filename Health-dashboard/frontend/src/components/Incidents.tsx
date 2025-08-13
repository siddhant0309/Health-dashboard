import React from 'react';
import { useServiceContext } from '../contexts/ServiceContext';
import { 
  AlertTriangle, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  MessageSquare,
  Calendar,
  User
} from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';
import toast from 'react-hot-toast';

const Incidents: React.FC = () => {
  const { incidents, services, resolveIncident, loading } = useServiceContext();

  const handleResolve = async (incidentId: number) => {
    try {
      await resolveIncident(incidentId);
      toast.success('Incident resolved successfully');
    } catch (err) {
      toast.error('Failed to resolve incident');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'investigating':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getServiceName = (serviceId: number) => {
    const service = services.find(s => s.id === serviceId);
    return service ? service.name : 'Unknown Service';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Incidents</h1>
          <p className="text-gray-600 mt-1">Track and manage service incidents</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm text-gray-600">Open Incidents</p>
            <p className="text-2xl font-bold text-red-600">
              {incidents.filter(i => i.status === 'open').length}
            </p>
          </div>
        </div>
      </div>

      {/* Incidents List */}
      <div className="space-y-4">
        {incidents.length === 0 ? (
          <div className="text-center py-12">
            <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No incidents reported</h3>
            <p className="text-gray-600">All services are running smoothly</p>
          </div>
        ) : (
          incidents.map((incident) => (
            <div
              key={incident.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {incident.title}
                  </h3>
                  <p className="text-gray-600 mb-3">{incident.description}</p>
                  
                  {/* Service Info */}
                  <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-4 h-4" />
                      {getServiceName(incident.service_id)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {format(new Date(incident.created_at), 'MMM dd, yyyy HH:mm')}
                    </span>
                  </div>
                </div>
                
                {/* Status and Severity */}
                <div className="flex flex-col gap-2 ml-4">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(incident.severity)}`}>
                    {incident.severity.charAt(0).toUpperCase() + incident.severity.slice(1)}
                  </span>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(incident.status)}`}>
                    {incident.status.charAt(0).toUpperCase() + incident.status.slice(1)}
                  </span>
                </div>
              </div>

              {/* Timeline */}
              <div className="border-t border-gray-100 pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>
                      Created {formatDistanceToNow(new Date(incident.created_at))} ago
                    </span>
                  </div>
                  
                  {incident.status === 'open' && (
                    <button
                      onClick={() => handleResolve(incident.id)}
                      className="btn-primary flex items-center gap-2"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Resolve Incident
                    </button>
                  )}
                  
                  {incident.status === 'resolved' && incident.resolved_at && (
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <CheckCircle className="w-4 h-4" />
                      <span>
                        Resolved {formatDistanceToNow(new Date(incident.resolved_at))} ago
                      </span>
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
          <p className="text-gray-600">Loading incidents...</p>
        </div>
      )}
    </div>
  );
};

export default Incidents;
