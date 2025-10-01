/**
 * Admin User Management
 * 
 * Simple user management interface for viewing users and their subscription status.
 * 
 * Features:
 * - User list with subscription details
 * - Search and filter users
 * - View user subscription history
 * - Basic user actions
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { 
  MagnifyingGlassIcon,
  EyeIcon,
  UserIcon,
  CreditCardIcon,
  CalendarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface User {
  id: string;
  email: string;
  phone: string;
  plan: string;
  status: 'active' | 'inactive' | 'suspended';
  createdAt: string;
  lastActive: string;
  alertsCount: number;
  revenue: number;
}

export default function AdminUsers() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPlan, setFilterPlan] = useState('all');
  const [isLoading, setIsLoading] = useState(true);

  // Mock admin check
  const isAdmin = user?.email === 'admin@mousealerts.com' || user?.id === 'admin-user';

  useEffect(() => {
    if (!isAdmin) return;
    loadUsers();
  }, [isAdmin]);

  useEffect(() => {
    filterUsers();
  }, [users, searchTerm, filterPlan]);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      
      // Mock data - in real implementation, fetch from API
      const mockUsers: User[] = [
        {
          id: 'user-1',
          email: 'sarah.johnson@email.com',
          phone: '+15551234567',
          plan: 'Premium',
          status: 'active',
          createdAt: '2024-01-15',
          lastActive: '2 hours ago',
          alertsCount: 8,
          revenue: 29.99
        },
        {
          id: 'user-2',
          email: 'mike.disney@email.com',
          phone: '+15559876543',
          plan: 'Family',
          status: 'active',
          createdAt: '2024-01-20',
          lastActive: '1 day ago',
          alertsCount: 15,
          revenue: 49.99
        },
        {
          id: 'user-3',
          email: 'lisa.princess@email.com',
          phone: '+15555555555',
          plan: 'Free',
          status: 'active',
          createdAt: '2024-02-01',
          lastActive: '3 days ago',
          alertsCount: 2,
          revenue: 0
        },
        {
          id: 'user-4',
          email: 'chris.magic@email.com',
          phone: '+15551111111',
          plan: 'Single Alert',
          status: 'active',
          createdAt: '2024-02-05',
          lastActive: '1 hour ago',
          alertsCount: 1,
          revenue: 4.99
        }
      ];

      setUsers(mockUsers);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterUsers = () => {
    let filtered = users;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(user => 
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.phone.includes(searchTerm)
      );
    }

    // Plan filter
    if (filterPlan !== 'all') {
      filtered = filtered.filter(user => user.plan === filterPlan);
    }

    setFilteredUsers(filtered);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />;
      case 'inactive':
        return <XCircleIcon className="w-5 h-5 text-gray-400" />;
      case 'suspended':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />;
      default:
        return <XCircleIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'Premium':
        return 'bg-blue-100 text-blue-800';
      case 'Family':
        return 'bg-green-100 text-green-800';
      case 'Free':
        return 'bg-gray-100 text-gray-800';
      case 'Single Alert':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600">You don't have permission to access user management.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4">
            <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
            <p className="text-sm text-gray-600">Manage users and their subscription status</p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="card mb-6">
          <div className="card-body">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search users by email or phone..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="form-input pl-10 w-full"
                  />
                </div>
              </div>
              <div className="md:w-48">
                <select
                  value={filterPlan}
                  onChange={(e) => setFilterPlan(e.target.value)}
                  className="form-select w-full"
                >
                  <option value="all">All Plans</option>
                  <option value="Free">Free</option>
                  <option value="Premium">Premium</option>
                  <option value="Family">Family</option>
                  <option value="Single Alert">Single Alert</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="card">
          <div className="card-body p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="loading-spinner w-8 h-8"></div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Plan
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Alerts
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Revenue
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Active
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {user.email}
                            </div>
                            <div className="text-sm text-gray-500">
                              {user.phone}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPlanColor(user.plan)}`}>
                            {user.plan}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(user.status)}
                            <span className="text-sm text-gray-900 capitalize">
                              {user.status}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {user.alertsCount}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${user.revenue.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.lastActive}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button className="text-primary-600 hover:text-primary-900">
                            <EyeIcon className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Summary Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">{users.length}</div>
              <div className="text-sm text-gray-600">Total Users</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">
                {users.filter(u => u.status === 'active').length}
              </div>
              <div className="text-sm text-gray-600">Active Users</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">
                {users.filter(u => u.plan !== 'Free').length}
              </div>
              <div className="text-sm text-gray-600">Paid Users</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-gray-900">
                ${users.reduce((sum, u) => sum + u.revenue, 0).toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Total Revenue</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
