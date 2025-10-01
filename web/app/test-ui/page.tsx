/**
 * Test UI Page
 * 
 * This page shows the dashboard UI without authentication for testing purposes.
 * It demonstrates all the design elements and styling.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AIPromptBar from '@/components/AIPromptBar';
import { 
  BellIcon, 
  PlusIcon, 
  UserIcon,
  ClockIcon,
  CheckCircleIcon,
  CalendarIcon,
  MapPinIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';

export default function TestUIPage() {
  const router = useRouter();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Mock data for demonstration
  useEffect(() => {
    setTimeout(() => {
      setAlerts([
        {
          id: 1,
          restaurant: 'Be Our Guest Restaurant',
          park: 'Magic Kingdom',
          date: '2024-01-15',
          time: '7:00 PM',
          partySize: 4,
          status: 'active',
          created: '2 days ago'
        },
        {
          id: 2,
          restaurant: 'Cinderella\'s Royal Table',
          park: 'Magic Kingdom',
          date: '2024-01-20',
          time: '6:30 PM',
          partySize: 2,
          status: 'active',
          created: '1 week ago'
        },
        {
          id: 3,
          restaurant: 'California Grill',
          park: 'Contemporary Resort',
          date: '2024-01-25',
          time: '9:00 PM',
          partySize: 2,
          status: 'active',
          created: '3 days ago'
        }
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);

  const handleCreateAlert = () => {
    router.push('/alerts/create');
  };

  return (
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
                <span>+15551234567</span>
              </div>
              <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors">
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
  );
}
