import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Services from './components/Services';
import Incidents from './components/Incidents';
import Alerts from './components/Alerts';
import Metrics from './components/Metrics';
import { ServiceProvider } from './contexts/ServiceContext';

function App() {
  return (
    <ServiceProvider>
      <Router>
        <div className="flex h-screen bg-gray-50">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/services" element={<Services />} />
              <Route path="/incidents" element={<Incidents />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/metrics" element={<Metrics />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ServiceProvider>
  );
}

export default App;
