/**
 * Admin System Health
 * 
 * Simple system monitoring interface for checking system health and performance.
 * 
 * Features:
 * - API status monitoring
 * - Error rate tracking
 * - Performance metrics
 * - System actions
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  ServerIcon,
  DatabaseIcon,
  BellIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

interface SystemHealth {
  apis: {
    auth: 'healthy' | 'warning' | 'error';
    alerts: 'healthy' | 'warning' | 'error';
    billing: 'healthy' | 'warning' | 'error';
    scraping: 'healthy' | 'warning' | 'error';
  };
  database: {
    status: 'healthy' | 'warning' | 'error';
    responseTime: number;
    connections: number;
  };
  services: {
    webScraper: 'running' | 'stopped' | 'error';
    notifications: 'running' | 'stopped' | 'error';
    backgroundSync: 'running' | 'stopped' | 'error';
  };
  metrics: {
    uptime: string;
    errorRate: number;
    responseTime: number;
    lastScrape: string;
  };
}

export default function AdminSystem() {
  const { user } = useAuth();
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState<Date>(new Date());

  // Mock admin check
  const isAdmin = user?.email === 'admin@mousealerts.com' || user?.id === 'admin-user';

  useEffect(() => {
    if (!isAdmin) return;
    loadSystemHealth();
    
    // Refresh every 30 seconds
    const interval = setInterval(loadSystemHealth, 30000);
    return () => clearInterval(interval);
  }, [isAdmin]);

  const loadSystemHealth = async () => {
    try {
      setIsLoading(true);
      
      // Mock data - in real implementation, fetch from API
      const mockHealth: SystemHealth = {
        apis: {
          auth: 'healthy',
          alerts: 'healthy',
          billing: 'warning',
          scraping: 'healthy'
        },
        database: {
          status: 'healthy',
          responseTime: 45,
          connections: 12
        },
        services: {
          webScraper: 'running',
          notifications: 'running',
          backgroundSync: 'running'
        },
        metrics: {
          uptime: '99.9%',
          errorRate: 0.8,
          responseTime: 120,
          lastScrape: '2 minutes ago'
        }
      };

      setHealth(mockHealth);
      setLastChecked(new Date());
    } catch (error) {
      console.error('Failed to load system health:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'running':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />;
      case 'warning':
        return <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />;
      case 'error':
      case 'stopped':
        return <XCircleIcon className="w-5 h-5 text-red-600" />;
      default:
        return <XCircleIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'running':
        return 'text-green-600';
      case 'warning':
        return 'text-yellow-600';
      case 'error':
      case 'stopped':
        return 'text-red-600';
      default:
        return 'text-gray-400';
    }
  };

  const handleSystemAction = async (action: string) => {
    try {
      console.log(`Executing system action: ${action}`);
      // In real implementation, call API
      // await fetch(`/api/admin/system/${action}`, { method: 'POST' });
    } catch (error) {
      console.error(`Failed to execute ${action}:`, error);
    }
  };

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600">You don't have permission to access system monitoring.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">System Health</h1>
              <p className="text-sm text-gray-600">
                Last checked: {lastChecked.toLocaleTimeString()}
              </p>
            </div>
            <button
              onClick={loadSystemHealth}
              className="btn btn-outline btn-sm"
            >
              <ArrowPathIcon className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">{health?.metrics.uptime}</div>
              <div className="text-sm text-gray-600">Uptime</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">{health?.metrics.errorRate}%</div>
              <div className="text-sm text-gray-600">Error Rate</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">{health?.metrics.responseTime}ms</div>
              <div className="text-sm text-gray-600">Response Time</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">{health?.metrics.lastScrape}</div>
              <div className="text-sm text-gray-600">Last Scrape</div>
            </div>
          </div>
        </div>

        {/* API Status */}
        <div className="card mb-8">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">API Status</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ServerIcon className="w-5 h-5 text-gray-600" />
                  <span className="text-sm font-medium">Authentication</span>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(health?.apis.auth || 'error')}
                  <span className={`text-sm font-medium ${getStatusColor(health?.apis.auth || 'error')}`}>
                    {health?.apis.auth || 'error'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <BellIcon className="w-5 h-5 text-gray-600" />
                  <span className="text-sm font-medium">Alerts API</span>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(health?.apis.alerts || 'error')}
                  <span className={`text-sm font-medium ${getStatusColor(health?.apis.alerts || 'error')}`}>
                    {health?.apis.alerts || 'error'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <GlobeAltIcon className="w-5 h-5 text-gray-600" />
                  <span className="text-sm font-medium">Billing API</span>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(health?.apis.billing || 'error')}
                  <span className={`text-sm font-medium ${getStatusColor(health?.apis.billing || 'error')}`}>
                    {health?.apis.billing || 'error'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ArrowPathIcon className="w-5 h-5 text-gray-600" />
                  <span className="text-sm font-medium">Scraping API</span>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(health?.apis.scraping || 'error')}
                  <span className={`text-sm font-medium ${getStatusColor(health?.apis.scraping || 'error')}`}>
                    {health?.apis.scraping || 'error'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Services Status */}
        <div className="card mb-8">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Services Status</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ArrowPathIcon className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-sm font-medium">Web Scraper</div>
                    <div className="text-xs text-gray-500">Monitors Disney availability</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(health?.services.webScraper || 'error')}
                  <span className={`text-sm font-medium ${getStatusColor(health?.services.webScraper || 'error')}`}>
                    {health?.services.webScraper || 'error'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <BellIcon className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-sm font-medium">Notification Service</div>
                    <div className="text-xs text-gray-500">Sends alerts to users</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(health?.services.notifications || 'error')}
                  <span className={`text-sm font-medium ${getStatusColor(health?.services.notifications || 'error')}`}>
                    {health?.services.notifications || 'error'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <ClockIcon className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-sm font-medium">Background Sync</div>
                    <div className="text-xs text-gray-500">Processes alerts in background</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(health?.services.backgroundSync || 'error')}
                  <span className={`text-sm font-medium ${getStatusColor(health?.services.backgroundSync || 'error')}`}>
                    {health?.services.backgroundSync || 'error'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Database Status */}
        <div className="card mb-8">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">Database Status</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{health?.database.responseTime}ms</div>
                <div className="text-sm text-gray-600">Response Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{health?.database.connections}</div>
                <div className="text-sm text-gray-600">Active Connections</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center space-x-2">
                  {getStatusIcon(health?.database.status || 'error')}
                  <span className={`text-lg font-semibold ${getStatusColor(health?.database.status || 'error')}`}>
                    {health?.database.status || 'error'}
                  </span>
                </div>
                <div className="text-sm text-gray-600">Status</div>
              </div>
            </div>
          </div>
        </div>

        {/* System Actions */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900">System Actions</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button
                onClick={() => handleSystemAction('restart-scraper')}
                className="btn btn-outline"
              >
                <ArrowPathIcon className="w-4 h-4" />
                Restart Scraper
              </button>
              <button
                onClick={() => handleSystemAction('restart-notifications')}
                className="btn btn-outline"
              >
                <BellIcon className="w-4 h-4" />
                Restart Notifications
              </button>
              <button
                onClick={() => handleSystemAction('clear-cache')}
                className="btn btn-outline"
              >
                <ClockIcon className="w-4 h-4" />
                Clear Cache
              </button>
              <button
                onClick={() => handleSystemAction('test-system')}
                className="btn btn-outline"
              >
                <CheckCircleIcon className="w-4 h-4" />
                Test System
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
