import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Types
export interface Service {
  id: number;
  name: string;
  url: string;
  status: 'healthy' | 'degraded' | 'down' | 'unknown';
  last_check: string;
  uptime: number;
  response_time: number;
  error_count: number;
  total_checks: number;
}

export interface Metric {
  timestamp: string;
  response_time: number;
  status_code: number;
  error: boolean;
  uptime: number;
}

export interface Incident {
  id: number;
  service_id: number;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved';
  created_at: string;
  resolved_at?: string;
}

export interface Alert {
  id: number;
  service_id: number;
  type: string;
  message: string;
  threshold: number;
  triggered_at: string;
  resolved_at?: string;
}

export interface DashboardStats {
  total_services: number;
  healthy_services: number;
  down_services: number;
  open_incidents: number;
  avg_response_time: number;
  timestamp: string;
}

interface ServiceContextType {
  services: Service[];
  incidents: Incident[];
  alerts: Alert[];
  stats: DashboardStats | null;
  loading: boolean;
  error: string | null;
  fetchServices: () => Promise<void>;
  fetchIncidents: () => Promise<void>;
  fetchAlerts: () => Promise<void>;
  fetchStats: () => Promise<void>;
  addService: (name: string, url: string) => Promise<void>;
  resolveIncident: (incidentId: number) => Promise<void>;
  refreshData: () => Promise<void>;
}

const ServiceContext = createContext<ServiceContextType | undefined>(undefined);

export const useServiceContext = () => {
  const context = useContext(ServiceContext);
  if (context === undefined) {
    throw new Error('useServiceContext must be used within a ServiceProvider');
  }
  return context;
};

interface ServiceProviderProps {
  children: ReactNode;
}

export const ServiceProvider: React.FC<ServiceProviderProps> = ({ children }) => {
  const [services, setServices] = useState<Service[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  const fetchServices = async () => {
    try {
      const response = await axios.get(`${API_BASE}/services`);
      setServices(response.data);
    } catch (err) {
      console.error('Error fetching services:', err);
      setError('Failed to fetch services');
    }
  };

  const fetchIncidents = async () => {
    try {
      const response = await axios.get(`${API_BASE}/incidents`);
      setIncidents(response.data);
    } catch (err) {
      console.error('Error fetching incidents:', err);
      setError('Failed to fetch incidents');
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/alerts`);
      setAlerts(response.data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Failed to fetch alerts');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/dashboard/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Error fetching stats:', err);
      setError('Failed to fetch dashboard stats');
    }
  };

  const addService = async (name: string, url: string) => {
    try {
      const response = await axios.post(`${API_BASE}/services`, { name, url });
      await fetchServices();
      return response.data;
    } catch (err) {
      console.error('Error adding service:', err);
      throw new Error('Failed to add service');
    }
  };

  const resolveIncident = async (incidentId: number) => {
    try {
      await axios.post(`${API_BASE}/incidents/${incidentId}/resolve`);
      await fetchIncidents();
      await fetchStats();
    } catch (err) {
      console.error('Error resolving incident:', err);
      throw new Error('Failed to resolve incident');
    }
  };

  const refreshData = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([
        fetchServices(),
        fetchIncidents(),
        fetchAlerts(),
        fetchStats(),
      ]);
    } catch (err) {
      console.error('Error refreshing data:', err);
      setError('Failed to refresh data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(refreshData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const value: ServiceContextType = {
    services,
    incidents,
    alerts,
    stats,
    loading,
    error,
    fetchServices,
    fetchIncidents,
    fetchAlerts,
    fetchStats,
    addService,
    resolveIncident,
    refreshData,
  };

  return (
    <ServiceContext.Provider value={value}>
      {children}
    </ServiceContext.Provider>
  );
};
