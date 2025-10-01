/**
 * Admin Dashboard
 * 
 * Simple admin interface for monitoring MouseAlerts system.
 * Provides essential metrics without overengineering.
 * 
 * Features:
 * - User count and subscription breakdown
 * - Revenue metrics (MRR, conversion rates)
 * - System health status
 * - Active alerts monitoring
 * - Quick system actions
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { 
  UsersIcon,
  CurrencyDollarIcon,
  BellIcon,
  HeartIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  EyeIcon,
  UserGroupIcon,
  CreditCardIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface AdminStats {
  users: {
    total: number;
    active: number;
    free: number;
    premium: number;
    family: number;
    singleAlert: number;
  };
  revenue: {
    mrr: number;
    totalRevenue: number;
    conversionRate: number;
    churnRate: number;
  };
  alerts: {
    active: number;
    total: number;
    successRate: number;
    recentActivity: number;
  };
  system: {
    status: 'healthy' | 'warning' | 'error';
    lastScrape: string;
    errorRate: number;
    uptime: string;
  };
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Check admin access - in production, this would call the API
  const isAdmin = user?.email === 'admin@mousealerts.com' || user?.id === 'admin-user';

  useEffect(() => {
    if (!isAdmin) {
      return;
    }

    loadAdminStats();
    
    // Refresh stats every 30 seconds
    const interval = setInterval(loadAdminStats, 30000);
    return () => clearInterval(interval);
  }, [isAdmin]);

  const loadAdminStats = async () => {
    try {
      setIsLoading(true);
      
      // Mock data - in real implementation, fetch from API
      const mockStats: AdminStats = {
        users: {
          total: 127,
          active: 89,
          free: 45,
          premium: 32,
          family: 8,
          singleAlert: 4
        },
        revenue: {
          mrr: 2847.50,
          totalRevenue: 8532.75,
          conversionRate: 12.5,
          churnRate: 3.2
        },
        alerts: {
          active: 156,
          total: 423,
          successRate: 87.3,
          recentActivity: 12
        },
        system: {
          status: 'healthy',
          lastScrape: '2 minutes ago',
          errorRate: 0.8,
          uptime: '99.9%'
        }
      };

      setStats(mockStats);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to load admin stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    loadAdminStats();
  };

  const handleSystemAction = async (action: string) => {
    try {
      // Mock system actions - in real implementation, call API
      console.log(`Executing system action: ${action}`);
      // await fetch(`/api/admin/actions/${action}`, { method: 'POST' });
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
          <p className="text-gray-600">You don't have permission to access the admin dashboard.</p>
        </div>
      </div>
    );
  }

  if (isLoading && !stats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="loading-spinner w-8 h-8"></div>
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
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <nav className="flex space-x-4">
                <a href="/admin" className="text-primary-600 font-medium">Dashboard</a>
                <a href="/admin/users" className="text-gray-600 hover:text-gray-900">Users</a>
                <a href="/admin/system" className="text-gray-600 hover:text-gray-900">System</a>
              </nav>
              <button
                onClick={handleRefresh}
                className="btn btn-outline btn-sm"
              >
                <ArrowPathIcon className="w-4 h-4" />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Users */}
          <div className="card">
            <div className="card-body">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Users</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.users.total}</p>
                </div>
                <UsersIcon className="w-8 h-8 text-blue-600" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-green-600">
                  {stats?.users.active} active
                </span>
              </div>
            </div>
          </div>

          {/* Revenue */}
          <div className="card">
            <div className="card-body">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${stats?.revenue.mrr.toLocaleString()}
                  </p>
                </div>
                <CurrencyDollarIcon className="w-8 h-8 text-green-600" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  {stats?.revenue.conversionRate}% conversion
                </span>
              </div>
            </div>
          </div>

          {/* Alerts */}
          <div className="card">
            <div className="card-body">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.alerts.active}</p>
                </div>
                <BellIcon className="w-8 h-8 text-purple-600" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-green-600">
                  {stats?.alerts.successRate}% success rate
                </span>
              </div>
            </div>
          </div>

          {/* System Health */}
          <div className="card">
            <div className="card-body">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">System Status</p>
                  <div className="flex items-center space-x-2">
                    {stats?.system.status === 'healthy' ? (
                      <CheckCircleIcon className="w-5 h-5 text-green-600" />
                    ) : (
                      <ExclamationTriangleIcon className="w-5 h-5 text-yellow-600" />
                    )}
                    <span className="text-lg font-semibold capitalize">
                      {stats?.system.status}
                    </span>
                  </div>
                </div>
                <HeartIcon className="w-8 h-8 text-red-600" />
              </div>
              <div className="mt-2">
                <span className="text-sm text-gray-600">
                  {stats?.system.uptime} uptime
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* User Breakdown */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">User Breakdown</h3>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                    <span className="text-sm font-medium">Free Plan</span>
                  </div>
                  <span className="text-sm text-gray-600">{stats?.users.free} users</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-medium">Premium Plan</span>
                  </div>
                  <span className="text-sm text-gray-600">{stats?.users.premium} users</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium">Family Plan</span>
                  </div>
                  <span className="text-sm text-gray-600">{stats?.users.family} users</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                    <span className="text-sm font-medium">Single Alert</span>
                  </div>
                  <span className="text-sm text-gray-600">{stats?.users.singleAlert} users</span>
                </div>
              </div>
            </div>
          </div>

          {/* System Health */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
            </div>
            <div className="card-body">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Last Web Scrape</span>
                  <span className="text-sm text-gray-600">{stats?.system.lastScrape}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Error Rate</span>
                  <span className="text-sm text-gray-600">{stats?.system.errorRate}%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Uptime</span>
                  <span className="text-sm text-gray-600">{stats?.system.uptime}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Recent Activity</span>
                  <span className="text-sm text-gray-600">{stats?.alerts.recentActivity} alerts</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            </div>
            <div className="card-body">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => handleSystemAction('restart-scraper')}
                  className="btn btn-outline"
                >
                  <ArrowPathIcon className="w-4 h-4" />
                  Restart Scraper
                </button>
                <button
                  onClick={() => handleSystemAction('clear-cache')}
                  className="btn btn-outline"
                >
                  <ClockIcon className="w-4 h-4" />
                  Clear Cache
                </button>
                <button
                  onClick={() => handleSystemAction('test-notifications')}
                  className="btn btn-outline"
                >
                  <BellIcon className="w-4 h-4" />
                  Test Notifications
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
