/**
 * User Dashboard Page
 * 
 * This is the main dashboard page that users see after logging in.
 * It provides access to all user features including alert management,
 * account settings, and subscription information.
 * 
 * Features:
 * - Protected route (requires authentication)
 * - User profile information
 * - Alert management interface
 * - Quick actions and navigation
 * - Subscription status and upgrade options
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import ProtectedRoute from '@/components/ProtectedRoute';
import AIPromptBar from '@/components/AIPromptBar';
import { PlanProvider } from '@/lib/plan';
import { PlanUsageDisplay, UpgradeSuggestions } from '@/components/PlanEnforcement';
import { 
  BellIcon, 
  PlusIcon, 
  CogIcon, 
  UserIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CalendarIcon,
  MapPinIcon,
  ArrowRightOnRectangleIcon,
  CreditCardIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateAlert, setShowCreateAlert] = useState(false);

  // For testing: Set up mock user if not authenticated
  useEffect(() => {
    if (!user && !isLoading) {
      const mockUser = {
        id: 'mock-user-123',
        phone: '+15551234567',
        email: 'test@mousealerts.com',
        plan: 'free',
        created_at: new Date().toISOString(),
      };
      localStorage.setItem('auth_token', 'mock-jwt-token-123');
      localStorage.setItem('user', JSON.stringify(mockUser));
      window.location.reload();
    }
  }, [user, isLoading]);

  // Fetch alerts from API
  useEffect(() => {
    const fetchAlerts = async () => {
      if (!user) {
        setIsLoading(false);
        return;
      }

      try {
        const authToken = localStorage.getItem('auth_token');
        if (!authToken) {
          setIsLoading(false);
          return;
        }

        const response = await fetch('/api/alerts', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          // Transform API response to match frontend format
          const transformedAlerts = data.map((alert: any) => {
            // Handle date formatting - API returns datetime string
            const alertDate = alert.date ? new Date(alert.date) : null;
            const dateStr = alertDate ? alertDate.toISOString().split('T')[0] : '';
            
            // Format time range
            const timeStr = alert.time_start && alert.time_end 
              ? `${alert.time_start} - ${alert.time_end}`
              : alert.time_start || 'Any time';
            
            return {
              id: alert.id,
              restaurant: alert.venue || 'Unknown Restaurant', // API uses 'venue', frontend expects 'restaurant'
              park: alert.park || 'Unknown Park',
              date: dateStr,
              time: timeStr,
              partySize: alert.party_size || 2,
              status: alert.status || 'active',
              created: alert.created_at ? new Date(alert.created_at).toLocaleDateString() : 'Recently'
            };
          });
          setAlerts(transformedAlerts);
        } else {
          console.error('Failed to fetch alerts:', response.status);
          // If unauthorized, user might need to re-login
          if (response.status === 401) {
            toast.error('Please log in again');
            router.push('/auth/login');
          }
        }
      } catch (error) {
        console.error('Error fetching alerts:', error);
        toast.error('Failed to load alerts');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAlerts();
  }, [user, router]);

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
    } catch (error) {
      toast.error('Failed to logout');
    }
  };

  const handleCreateAlert = () => {
    router.push('/alerts/create');
  };

  // For testing: Show dashboard directly if no user
  if (!user && !isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
          <div className="text-center">
            <div className="loading-spinner mx-auto mb-4 w-6 h-6" />
            <p className="text-gray-600">Setting up mock user...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <PlanProvider>
        <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 text-primary-500">
                  ✨
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">MouseAlerts</h1>
                  <p className="text-sm text-gray-500">Disney Dining Alerts</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <UserIcon className="w-4 h-4" />
                  <span>{user?.phone || 'User'}</span>
                </div>
                <button
                  onClick={() => router.push('/billing')}
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <CreditCardIcon className="w-4 h-4" />
                  <span>Billing</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                >
                  <ArrowRightOnRectangleIcon className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <div className="card-glass p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    Welcome back! 👋
                  </h2>
                  <p className="text-gray-600 text-lg">
                    Ready to find your perfect Disney dining experience?
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleCreateAlert}
                    className="btn btn-primary flex items-center space-x-2"
                  >
                    <PlusIcon className="w-5 h-5" />
                    <span>Create Alert</span>
                  </button>
                  <button
                    onClick={() => router.push('/ai-prompt')}
                    className="btn btn-accent flex items-center space-x-2"
                  >
                    <span className="w-5 h-5">💬</span>
                    <span>AI Prompt Bar</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* AI Prompt Bar Section */}
          <div className="mb-8">
            <div className="card card-gradient">
              <div className="card-body">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-white/20 rounded-lg">
                    <div className="w-6 h-6 text-white">💬</div>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">AI Prompt Bar</h3>
                    <p className="text-white/80">Describe your dining request in natural language</p>
                  </div>
                </div>
                
                <AIPromptBar
                  onSuggestionSelect={(suggestion) => {
                    // Navigate to alert creation with pre-filled data
                    const params = new URLSearchParams({
                      restaurant: suggestion.name,
                      park: suggestion.park,
                      date: new Date().toISOString().split('T')[0],
                      party_size: '2',
                    })
                    router.push(`/alerts/create?${params.toString()}`)
                  }}
                  placeholder="Try: 'Princess dining Thursday at 7pm for 4 people' or 'Something romantic with fireworks view'"
                  compact={true}
                />
              </div>
            </div>
          </div>

            {/* Plan Information */}
            <div className="mb-8">
              <PlanUsageDisplay />
              <UpgradeSuggestions />
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="card p-6">
              <div className="flex items-center">
                <div className="p-3 bg-primary-100 rounded-xl">
                  <BellIcon className="w-6 h-6 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                  <p className="text-2xl font-bold text-gray-900">{alerts.length}</p>
                </div>
              </div>
            </div>
            
            <div className="card p-6">
              <div className="flex items-center">
                <div className="p-3 bg-secondary-100 rounded-xl">
                  <CheckCircleIcon className="w-6 h-6 text-secondary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Found Reservations</p>
                  <p className="text-2xl font-bold text-gray-900">0</p>
                </div>
              </div>
            </div>
            
            <div className="card p-6">
              <div className="flex items-center">
                <div className="p-3 bg-accent-100 rounded-xl">
                  <ClockIcon className="w-6 h-6 text-accent-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Days Monitoring</p>
                  <p className="text-2xl font-bold text-gray-900">7</p>
                </div>
              </div>
            </div>
          </div>

          {/* Active Alerts */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">Your Active Alerts</h3>
              <button
                onClick={handleCreateAlert}
                className="btn btn-outline flex items-center space-x-2"
              >
                <PlusIcon className="w-4 h-4" />
                <span>Add Alert</span>
              </button>
            </div>

            {isLoading ? (
              <div className="card p-8 text-center">
                <div className="loading-spinner mx-auto mb-4 w-6 h-6" />
                <p className="text-gray-600">Loading your alerts...</p>
              </div>
            ) : alerts.length === 0 ? (
              <div className="card p-8 text-center">
                <BellIcon className="w-6 h-6 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 mb-2">No alerts yet</h4>
                <p className="text-gray-600 mb-6">
                  Create your first dining alert to get started with MouseAlerts!
                </p>
                <button
                  onClick={handleCreateAlert}
                  className="btn btn-primary"
                >
                  Create Your First Alert
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {alerts.map((alert) => (
                  <div key={alert.id} className="card p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="text-lg font-semibold text-gray-900">
                            {alert.restaurant}
                          </h4>
                          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                            Active
                          </span>
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <div className="flex items-center space-x-1">
                            <MapPinIcon className="w-4 h-4" />
                            <span>{alert.park}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <CalendarIcon className="w-4 h-4" />
                            <span>{alert.date} at {alert.time}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <UserIcon className="w-4 h-4" />
                            <span>{alert.partySize} people</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button 
                          onClick={() => router.push('/alerts')}
                          className="btn btn-ghost btn-sm"
                        >
                          Manage
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-primary-500 rounded-full" />
                <span className="text-gray-600">Created alert for Be Our Guest Restaurant</span>
                <span className="text-gray-400">2 days ago</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-secondary-500 rounded-full" />
                <span className="text-gray-600">Account created and verified</span>
                <span className="text-gray-400">1 week ago</span>
              </div>
            </div>
          </div>
        </main>
      </div>
      </PlanProvider>
    </ProtectedRoute>
  );
}
