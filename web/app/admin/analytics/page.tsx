"use client";

import { useState, useEffect } from "react";
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  BellIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from "@heroicons/react/24/outline";

interface RevenueAnalytics {
  mrr: number;
  conversion_rate: number;
  monthly_revenue: number;
  churn_rate: number;
  total_users: number;
  paid_users: number;
  active_subscriptions: number;
}

interface AlertMetrics {
  total_alerts: number;
  active_alerts: number;
  paused_alerts: number;
  expired_alerts: number;
  success_rate: number;
  recent_alerts: number;
  run_success_rate: number;
  avg_response_time: number;
}

interface SystemHealth {
  api_status: string;
  db_status: string;
  error_rate: number;
  last_success_time: string | null;
  pending_alerts: number;
  uptime_percentage: number;
}

export default function AnalyticsPage() {
  const [revenue, setRevenue] = useState<RevenueAnalytics | null>(null);
  const [alerts, setAlerts] = useState<AlertMetrics | null>(null);
  const [system, setSystem] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/analytics/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch analytics');
      }

      const data = await response.json();
      setRevenue(data.revenue);
      setAlerts(data.alerts);
      setSystem(data.system);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white p-6 rounded-lg shadow">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mr-3" />
              <div>
                <h3 className="text-lg font-medium text-red-800">Error Loading Analytics</h3>
                <p className="text-red-600 mt-1">{error}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Revenue metrics, alert monitoring, and system health</p>
        </div>

        {/* Revenue Analytics */}
        {revenue && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <CurrencyDollarIcon className="h-6 w-6 mr-2" />
              Revenue Analytics
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Monthly Recurring Revenue</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(revenue.mrr)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Conversion Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{formatPercentage(revenue.conversion_rate)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <CurrencyDollarIcon className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Monthly Revenue</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(revenue.monthly_revenue)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Churn Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{formatPercentage(revenue.churn_rate)}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Total Users</p>
                <p className="text-3xl font-bold text-gray-900">{revenue.total_users.toLocaleString()}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Paid Users</p>
                <p className="text-3xl font-bold text-gray-900">{revenue.paid_users.toLocaleString()}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Active Subscriptions</p>
                <p className="text-3xl font-bold text-gray-900">{revenue.active_subscriptions.toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}

        {/* Alert Monitoring */}
        {alerts && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <BellIcon className="h-6 w-6 mr-2" />
              Alert Monitoring
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Total Alerts</p>
                <p className="text-3xl font-bold text-gray-900">{alerts.total_alerts.toLocaleString()}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Active Alerts</p>
                <p className="text-3xl font-bold text-green-600">{alerts.active_alerts.toLocaleString()}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Success Rate</p>
                <p className="text-3xl font-bold text-blue-600">{formatPercentage(alerts.success_rate)}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Recent Alerts (7d)</p>
                <p className="text-3xl font-bold text-purple-600">{alerts.recent_alerts.toLocaleString()}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Paused Alerts</p>
                <p className="text-2xl font-bold text-yellow-600">{alerts.paused_alerts.toLocaleString()}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Expired Alerts</p>
                <p className="text-2xl font-bold text-red-600">{alerts.expired_alerts.toLocaleString()}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Run Success Rate</p>
                <p className="text-2xl font-bold text-green-600">{formatPercentage(alerts.run_success_rate)}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Avg Response Time</p>
                <p className="text-2xl font-bold text-blue-600">{alerts.avg_response_time.toFixed(0)}ms</p>
              </div>
            </div>
          </div>
        )}

        {/* System Health */}
        {system && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <CheckCircleIcon className="h-6 w-6 mr-2" />
              System Health
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">API Status</p>
                    <p className="text-lg font-semibold text-gray-900">{system.api_status}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(system.api_status)}`}>
                    {system.api_status}
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Database Status</p>
                    <p className="text-lg font-semibold text-gray-900">{system.db_status}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(system.db_status)}`}>
                    {system.db_status}
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ClockIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Uptime</p>
                    <p className="text-2xl font-bold text-gray-900">{formatPercentage(system.uptime_percentage)}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Error Rate</p>
                <p className="text-2xl font-bold text-red-600">{formatPercentage(system.error_rate)}</p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Pending Alerts</p>
                <p className="text-2xl font-bold text-yellow-600">{system.pending_alerts.toLocaleString()}</p>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <p className="text-sm font-medium text-gray-500">Last Success</p>
                <p className="text-lg font-semibold text-gray-900">
                  {system.last_success_time 
                    ? new Date(system.last_success_time).toLocaleString()
                    : 'Never'
                  }
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Refresh Button */}
        <div className="mt-8 flex justify-center">
          <button
            onClick={fetchAnalytics}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Analytics
          </button>
        </div>
      </div>
    </div>
  );
}
