/**
 * Billing Management Page
 * 
 * This page allows users to:
 * - View current subscription plan
 * - Upgrade/downgrade plans
 * - Manage payment methods
 * - View billing history
 * - Access Stripe customer portal
 * 
 * Features:
 * - Plan comparison table
 * - Stripe checkout integration
 * - Subscription status display
 * - Payment method management
 */

'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  CreditCardIcon,
  CheckCircleIcon,
  XMarkIcon,
  ArrowRightIcon,
  StarIcon,
  UserGroupIcon,
  BoltIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface Plan {
  id: string;
  name: string;
  price: number;
  interval: string;
  features: string[];
  limits: {
    alerts: number;
    notifications: string;
    support: string;
  };
  popular?: boolean;
}

const PLANS: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    interval: 'forever',
    features: [
      'Up to 3 active alerts',
      'Email notifications only',
      'Basic support',
      'Standard monitoring speed'
    ],
    limits: {
      alerts: 3,
      notifications: 'Email only',
      support: 'Basic'
    }
  },
  {
    id: 'single',
    name: 'Single Alert',
    price: 4.99,
    interval: 'one-time',
    features: [
      '1 active alert',
      'Email + SMS notifications',
      'Priority support',
      'Faster monitoring (5min intervals)',
      'AI Prompt Bar access',
      'Perfect for trying the service'
    ],
    limits: {
      alerts: 1,
      notifications: 'Email + SMS',
      support: 'Priority'
    }
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 9.99,
    interval: 'month',
    features: [
      'Up to 25 active alerts',
      'Email + SMS notifications',
      'Priority support',
      'Faster monitoring (5min intervals)',
      'AI Prompt Bar access',
      'Advanced filtering'
    ],
    limits: {
      alerts: 25,
      notifications: 'Email + SMS',
      support: 'Priority'
    },
    popular: true
  },
  {
    id: 'family',
    name: 'Family',
    price: 19.99,
    interval: 'month',
    features: [
      'Unlimited alerts',
      'All notification types',
      'Priority support',
      'Fastest monitoring (1min intervals)',
      'AI Prompt Bar access',
      'Advanced filtering',
      'Family sharing (up to 5 users)',
      'Custom alert templates'
    ],
    limits: {
      alerts: -1, // unlimited
      notifications: 'All types',
      support: 'Priority'
    }
  }
];

export default function BillingPage() {
  const { user } = useAuth();
  const [currentPlan, setCurrentPlan] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpgrading, setIsUpgrading] = useState<string | null>(null);

  useEffect(() => {
    // Mock current subscription data
    setTimeout(() => {
      setCurrentPlan({
        plan: 'free',
        status: 'active',
        current_period_end: null
      });
      setIsLoading(false);
    }, 1000);
  }, []);

  const handleUpgrade = async (planId: string) => {
    if (planId === 'free') return;
    
    setIsUpgrading(planId);
    try {
      // Mock API call to create checkout session
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In real implementation, this would redirect to Stripe checkout
      if (planId === 'single') {
        toast.success('Redirecting to single alert payment...');
      } else {
        toast.success(`Redirecting to ${planId} plan payment...`);
      }
      
      // Mock redirect to Stripe checkout
      // window.location.href = checkoutUrl;
    } catch (error) {
      toast.error('Failed to start upgrade process');
    } finally {
      setIsUpgrading(null);
    }
  };

  const handleManageSubscription = async () => {
    try {
      // Mock API call to get customer portal URL
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In real implementation, this would redirect to Stripe portal
      toast.success('Redirecting to subscription management...');
      
      // Mock redirect to Stripe portal
      // window.location.href = portalUrl;
    } catch (error) {
      toast.error('Failed to open subscription management');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4 w-8 h-8" />
          <p className="text-gray-600">Loading billing information...</p>
        </div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Billing & Plans</h1>
                <p className="text-gray-600 mt-1">Manage your subscription and payment methods</p>
              </div>
              {currentPlan?.plan !== 'free' && (
                <button
                  onClick={handleManageSubscription}
                  className="btn btn-outline flex items-center space-x-2"
                >
                  <CreditCardIcon className="w-5 h-5" />
                  <span>Manage Subscription</span>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Current Plan Status */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="card p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Current Plan</h2>
                <div className="flex items-center space-x-3 mt-2">
                  <span className="px-3 py-1 bg-primary-100 text-primary-800 text-sm font-medium rounded-full">
                    {currentPlan?.plan?.charAt(0).toUpperCase() + currentPlan?.plan?.slice(1)} Plan
                  </span>
                  <span className="text-sm text-gray-500">
                    {currentPlan?.status === 'active' ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Plan limits</p>
                <p className="text-lg font-semibold text-gray-900">
                  {currentPlan?.plan === 'free' ? '3 alerts' : 
                   currentPlan?.plan === 'premium' ? '25 alerts' : 'Unlimited alerts'}
                </p>
              </div>
            </div>
          </div>

          {/* Plans Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {PLANS.map((plan) => (
              <div
                key={plan.id}
                className={`card p-6 relative ${
                  plan.popular ? 'ring-2 ring-primary-500' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary-500 text-white px-3 py-1 text-sm font-medium rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <div className="flex items-center justify-center mb-2">
                    {plan.id === 'free' && <BoltIcon className="w-8 h-8 text-gray-400" />}
                    {plan.id === 'single' && <SparklesIcon className="w-8 h-8 text-accent-500" />}
                    {plan.id === 'premium' && <StarIcon className="w-8 h-8 text-primary-500" />}
                    {plan.id === 'family' && <UserGroupIcon className="w-8 h-8 text-secondary-500" />}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                  <div className="mt-2">
                    <span className="text-4xl font-bold text-gray-900">${plan.price}</span>
                    <span className="text-gray-500">/{plan.interval}</span>
                  </div>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center">
                      <CheckCircleIcon className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                      <span className="text-sm text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={isUpgrading === plan.id || plan.id === currentPlan?.plan}
                  className={`w-full btn ${
                    plan.id === currentPlan?.plan
                      ? 'btn-ghost cursor-not-allowed'
                      : plan.popular
                      ? 'btn-primary'
                      : 'btn-outline'
                  } flex items-center justify-center space-x-2`}
                >
                  {isUpgrading === plan.id ? (
                    <>
                      <div className="loading-spinner w-4 h-4" />
                      <span>Processing...</span>
                    </>
                  ) : plan.id === currentPlan?.plan ? (
                    <>
                      <CheckCircleIcon className="w-5 h-5" />
                      <span>Current Plan</span>
                    </>
                  ) : (
                    <>
                      <span>{plan.id === 'free' ? 'Downgrade' : 'Upgrade'}</span>
                      <ArrowRightIcon className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>

          {/* Billing History */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Billing History</h3>
            <div className="text-center py-8">
              <CreditCardIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No billing history available</p>
              <p className="text-sm text-gray-400 mt-1">
                Your payment history will appear here once you subscribe to a paid plan
              </p>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
