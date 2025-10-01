/**
 * Alerts Management Page
 * 
 * This page displays all user alerts with management capabilities.
 * Features:
 * - List of all user alerts
 * - Edit and delete functionality
 * - Alert status and details
 * - Quick actions and filters
 * - Responsive design for mobile and desktop
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  PlusIcon,
  PencilIcon,
  TrashIcon,
  BellIcon,
  CalendarIcon,
  MapPinIcon,
  UserGroupIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

export default function AlertsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [alerts, setAlerts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, active, expired

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
          created: '2 days ago',
          notifications: 0
        },
        {
          id: 2,
          restaurant: 'Cinderella\'s Royal Table',
          park: 'Magic Kingdom',
          date: '2024-01-20',
          time: '6:30 PM',
          partySize: 2,
          status: 'active',
          created: '1 week ago',
          notifications: 2
        },
        {
          id: 3,
          restaurant: 'Le Cellier Steakhouse',
          park: 'EPCOT',
          date: '2024-01-10',
          time: '8:00 PM',
          partySize: 6,
          status: 'expired',
          created: '2 weeks ago',
          notifications: 1
        },
        {
          id: 4,
          restaurant: 'California Grill',
          park: 'Contemporary Resort',
          date: '2024-01-25',
          time: '9:00 PM',
          partySize: 2,
          status: 'active',
          created: '3 days ago',
          notifications: 0
        },
        {
          id: 5,
          restaurant: 'Ohana',
          park: 'Polynesian Resort',
          date: '2024-01-18',
          time: '5:30 PM',
          partySize: 4,
          status: 'active',
          created: '5 days ago',
          notifications: 1
        },
        {
          id: 6,
          restaurant: 'The Hollywood Brown Derby',
          park: 'Hollywood Studios',
          date: '2024-01-12',
          time: '7:30 PM',
          partySize: 3,
          status: 'expired',
          created: '1 week ago',
          notifications: 0
        }
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);

  const handleEditAlert = (alertId: number) => {
    toast.success('Edit functionality coming soon!');
    // router.push(`/alerts/${alertId}/edit`);
  };

  const handleDeleteAlert = async (alertId: number) => {
    if (window.confirm('Are you sure you want to delete this alert?')) {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setAlerts(prev => prev.filter(alert => alert.id !== alertId));
        toast.success('Alert deleted successfully');
      } catch (error) {
        toast.error('Failed to delete alert');
      }
    }
  };

  const handleCreateAlert = () => {
    router.push('/alerts/create');
  };

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'active') return alert.status === 'active';
    if (filter === 'expired') return alert.status === 'expired';
    return true;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'expired':
        return <ExclamationTriangleIcon className="w-5 h-5 text-orange-500" />;
      default:
        return <BellIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between py-4">
              <div className="flex items-center space-x-3">
                <div className="magic-glow">
                  <SparklesIcon className="w-8 h-8 text-primary-500" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">My Alerts</h1>
                  <p className="text-sm text-gray-500">Manage your Disney dining alerts</p>
                </div>
              </div>
              
              <button
                onClick={handleCreateAlert}
                className="btn btn-primary flex items-center space-x-2"
              >
                <PlusIcon className="w-5 h-5" />
                <span>Create Alert</span>
              </button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Filters */}
          <div className="mb-6">
            <div className="flex space-x-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === 'all' 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                All ({alerts.length})
              </button>
              <button
                onClick={() => setFilter('active')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === 'active' 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Active ({alerts.filter(a => a.status === 'active').length})
              </button>
              <button
                onClick={() => setFilter('expired')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  filter === 'expired' 
                    ? 'bg-primary-500 text-white' 
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                }`}
              >
                Expired ({alerts.filter(a => a.status === 'expired').length})
              </button>
            </div>
          </div>

          {/* Alerts List */}
          {isLoading ? (
            <div className="card p-8 text-center">
              <div className="loading-spinner mx-auto mb-4 w-8 h-8" />
              <p className="text-gray-600">Loading your alerts...</p>
            </div>
          ) : filteredAlerts.length === 0 ? (
            <div className="card p-8 text-center">
              <BellIcon className="w-8 h-8 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {filter === 'all' ? 'No alerts yet' : `No ${filter} alerts`}
              </h3>
              <p className="text-gray-600 mb-6">
                {filter === 'all' 
                  ? 'Create your first dining alert to get started!'
                  : `You don't have any ${filter} alerts at the moment.`
                }
              </p>
              {filter === 'all' && (
                <button
                  onClick={handleCreateAlert}
                  className="btn btn-primary"
                >
                  Create Your First Alert
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAlerts.map((alert) => (
                <div key={alert.id} className="card p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {alert.restaurant}
                        </h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(alert.status)}`}>
                          {alert.status}
                        </span>
                        {getStatusIcon(alert.status)}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <MapPinIcon className="w-4 h-4" />
                          <span>{alert.park}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <CalendarIcon className="w-4 h-4" />
                          <span>{alert.date}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <ClockIcon className="w-4 h-4" />
                          <span>{alert.time}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <UserGroupIcon className="w-4 h-4" />
                          <span>{alert.partySize} people</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <BellIcon className="w-4 h-4" />
                          <span>{alert.notifications} notifications sent</span>
                        </div>
                        <div className="text-gray-500">
                          Created {alert.created}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => handleEditAlert(alert.id)}
                        className="btn btn-ghost btn-sm flex items-center space-x-1"
                      >
                        <PencilIcon className="w-4 h-4" />
                        <span>Edit</span>
                      </button>
                      <button
                        onClick={() => handleDeleteAlert(alert.id)}
                        className="btn btn-ghost btn-sm text-red-600 hover:text-red-700 flex items-center space-x-1"
                      >
                        <TrashIcon className="w-4 h-4" />
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
