import React, { useState, useEffect } from 'react';
import { useServiceContext } from '../contexts/ServiceContext';
import { 
  BarChart3, 
  TrendingUp, 
  Activity, 
  Clock,
  Download,
  Calendar
} from 'lucide-react';
import { format, subDays, startOfDay } from 'date-fns';
import axios from 'axios';

interface ServiceMetrics {
  service_id: number;
  timestamp: string;
  response_time: number;
  status_code: number;
  error: boolean;
  uptime: number;
}

const Metrics: React.FC = () => {
  const { services } = useServiceContext();
  const [selectedService, setSelectedService] = useState<number | null>(null);
  const [timeRange, setTimeRange] = useState('24h');
  const [metrics, setMetrics] = useState<ServiceMetrics[]>([]);
  const [loading, setLoading] = useState(false);

  const timeRanges = [
    { value: '1h', label: 'Last Hour' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
  ];

  useEffect(() => {
    if (selectedService) {
      fetchMetrics();
    }
  }, [selectedService, timeRange]);

  const fetchMetrics = async () => {
    if (!selectedService) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`/api/services/${selectedService}/metrics`);
      setMetrics(response.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getServiceName = (serviceId: number) => {
    const service = services.find(s => s.id === serviceId);
    return service ? service.name : 'Unknown Service';
  };

  const calculateStats = () => {
    if (metrics.length === 0) return null;

    const responseTimes = metrics.map(m => m.response_time).filter(t => t > 0);
    const errors = metrics.filter(m => m.error).length;
    const total = metrics.length;

    return {
      avgResponseTime: responseTimes.length > 0 ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length : 0,
      p50ResponseTime: responseTimes.length > 0 ? responseTimes.sort((a, b) => a - b)[Math.floor(responseTimes.length * 0.5)] : 0,
      p95ResponseTime: responseTimes.length > 0 ? responseTimes.sort((a, b) => a - b)[Math.floor(responseTimes.length * 0.95)] : 0,
      errorRate: total > 0 ? (errors / total) * 100 : 0,
      totalRequests: total,
      avgUptime: metrics.reduce((sum, m) => sum + m.uptime, 0) / metrics.length,
    };
  };

  const stats = calculateStats();

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Metrics</h1>
          <p className="text-gray-600 mt-1">Detailed performance metrics and analytics</p>
        </div>
        <div className="flex items-center gap-4">
          <select
            value={selectedService || ''}
            onChange={(e) => setSelectedService(e.target.value ? Number(e.target.value) : null)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select a service</option>
            {services.map((service) => (
              <option key={service.id} value={service.id}>
                {service.name}
              </option>
            ))}
          </select>
          
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {timeRanges.map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!selectedService ? (
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Select a service to view metrics</h3>
          <p className="text-gray-600">Choose a service from the dropdown above to see detailed performance data</p>
        </div>
      ) : (
        <>
          {/* Service Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {getServiceName(selectedService)}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {timeRange === '1h' ? '1 Hour' : 
                   timeRange === '24h' ? '24 Hours' :
                   timeRange === '7d' ? '7 Days' : '30 Days'}
                </div>
                <p className="text-sm text-gray-600">Time Range</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {metrics.length}
                </div>
                <p className="text-sm text-gray-600">Data Points</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {stats?.avgUptime.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">Average Uptime</p>
              </div>
            </div>
          </div>

          {/* Performance Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Activity className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.avgResponseTime.toFixed(3)}s
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">P50 Response Time</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.p50ResponseTime.toFixed(3)}s
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">P95 Response Time</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.p95ResponseTime.toFixed(3)}s
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <Activity className="w-6 h-6 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Error Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.errorRate.toFixed(2)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Metrics Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Raw Metrics Data</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Response Time
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Error
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Uptime
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-4 text-center">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                      </td>
                    </tr>
                  ) : metrics.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                        No metrics data available for the selected time range
                      </td>
                    </tr>
                  ) : (
                    metrics.map((metric, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {format(new Date(metric.timestamp), 'MMM dd, HH:mm:ss')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {metric.response_time.toFixed(3)}s
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {metric.status_code || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            metric.error 
                              ? 'bg-red-100 text-red-800' 
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {metric.error ? 'Yes' : 'No'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {metric.uptime.toFixed(1)}%
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Metrics;
