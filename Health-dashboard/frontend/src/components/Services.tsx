import React, { useState } from 'react';
import { useServiceContext } from '../contexts/ServiceContext';
import { 
  Plus, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Clock,
  Activity,
  TrendingUp,
  Globe,
  Edit,
  Trash2,
  Server
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import toast from 'react-hot-toast';

const Services: React.FC = () => {
  const { services, addService, loading } = useServiceContext();
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', url: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.url.trim()) {
      toast.error('Please fill in all fields');
      return;
    }

    setIsSubmitting(true);
    try {
      await addService(formData.name.trim(), formData.url.trim());
      setFormData({ name: '', url: '' });
      setShowAddForm(false);
      toast.success('Service added successfully');
    } catch (err) {
      toast.error('Failed to add service');
    } finally {
      setIsSubmitting(false);
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

  const getUptimeColor = (uptime: number) => {
    if (uptime >= 99) return 'text-success-600';
    if (uptime >= 95) return 'text-warning-600';
    return 'text-danger-600';
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Services</h1>
          <p className="text-gray-600 mt-1">Manage and monitor your cloud services</p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Service
        </button>
      </div>

      {/* Add Service Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Add New Service</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                Service Name
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., User Authentication API"
                required
              />
            </div>
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
                Service URL
              </label>
              <input
                type="url"
                id="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="https://api.example.com/health"
                required
              />
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Adding...' : 'Add Service'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false);
                  setFormData({ name: '', url: '' });
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Services Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {services.map((service) => (
          <div
            key={service.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{service.name}</h3>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Globe className="w-4 h-4" />
                  <span className="truncate">{service.url}</span>
                </div>
              </div>
              <div className="ml-4">
                {getStatusIcon(service.status)}
              </div>
            </div>

            {/* Status Badge */}
            <div className="mb-4">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(service.status)}`}>
                {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
              </span>
            </div>

            {/* Metrics */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Response Time
                </span>
                <span className="font-medium text-gray-900">
                  {service.response_time.toFixed(3)}s
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Uptime
                </span>
                <span className={`font-medium ${getUptimeColor(service.uptime)}`}>
                  {service.uptime.toFixed(1)}%
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Error Rate</span>
                <span className="font-medium text-gray-900">
                  {service.total_checks > 0 
                    ? ((service.error_count / service.total_checks) * 100).toFixed(1)
                    : 0}%
                </span>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-4 pt-4 border-t border-gray-100">
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>Last check: {formatDistanceToNow(new Date(service.last_check))} ago</span>
                <div className="flex gap-2">
                  <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-1 hover:bg-gray-100 rounded transition-colors text-danger-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {services.length === 0 && !loading && (
        <div className="text-center py-12">
          <Server className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No services configured</h3>
          <p className="text-gray-600 mb-6">
            Get started by adding your first cloud service to monitor
          </p>
          <button
            onClick={() => setShowAddForm(true)}
            className="btn-primary"
          >
            Add Your First Service
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading services...</p>
        </div>
      )}
    </div>
  );
};

export default Services;
