/**
 * Quick Alert Page - Ultra-Fast Single Alert Creation
 * 
 * This page is optimized for busy families who want to create
 * a single alert quickly without signing up for a subscription.
 * 
 * Features:
 * - One-page alert creation with payment
 * - Pre-filled smart defaults
 * - Mobile-optimized for on-the-go use
 * - Express checkout flow
 * - AI-powered restaurant suggestions
 * - Time-saving templates
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  ClockIcon,
  MapPinIcon,
  UserGroupIcon,
  CreditCardIcon,
  SparklesIcon,
  ArrowRightIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

// Quick templates for common family requests
const QUICK_TEMPLATES = [
  {
    id: 'princess-dining',
    title: '👸 Princess Dining',
    description: 'Cinderella\'s Royal Table, Be Our Guest',
    template: 'Princess character dining for 4 people'
  },
  {
    id: 'fireworks-dining',
    title: '🎆 Fireworks View',
    description: 'California Grill, Ohana',
    template: 'Dinner with fireworks view for 2 people'
  },
  {
    id: 'family-dinner',
    title: '👨‍👩‍👧‍👦 Family Dinner',
    description: 'Liberty Tree Tavern, Crystal Palace',
    template: 'Family-style dinner for 6 people'
  },
  {
    id: 'romantic-dinner',
    title: '💕 Date Night',
    description: 'Victoria & Albert\'s, California Grill',
    template: 'Romantic dinner for 2 people'
  }
];

export default function QuickAlertPage() {
  const router = useRouter();
  const [step, setStep] = useState(1); // 1: Template, 2: Details, 3: Payment
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [alertData, setAlertData] = useState({
    restaurant: '',
    date: '',
    time: '',
    partySize: 4,
    phone: '',
    email: ''
  });
  const [isProcessing, setIsProcessing] = useState(false);

  // Auto-fill current date and popular times
  useEffect(() => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    setAlertData(prev => ({
      ...prev,
      date: tomorrow.toISOString().split('T')[0],
      time: '19:00' // 7 PM default
    }));
  }, []);

  const handleTemplateSelect = (template: any) => {
    setSelectedTemplate(template);
    setStep(2);
  };

  const handleQuickCreate = async () => {
    setIsProcessing(true);
    try {
      // Simulate quick payment and alert creation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Alert created! You\'ll get notified when a table opens.');
      router.push('/quick-alert/success');
    } catch (error) {
      toast.error('Failed to create alert');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <SparklesIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Quick Alert</h1>
                <p className="text-sm text-gray-500">One-time alert • $4.99</p>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              Step {step} of 3
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {step === 1 && (
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              What kind of dining experience are you looking for?
            </h2>
            <p className="text-gray-600 mb-8">
              Choose a template to get started quickly, or create a custom alert
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {QUICK_TEMPLATES.map((template) => (
                <button
                  key={template.id}
                  onClick={() => handleTemplateSelect(template)}
                  className="card p-6 text-left hover:ring-2 hover:ring-primary-500 transition-all"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {template.title}
                  </h3>
                  <p className="text-gray-600 mb-3">{template.description}</p>
                  <div className="text-sm text-primary-600 font-medium">
                    {template.template}
                  </div>
                </button>
              ))}
            </div>
            
            <button
              onClick={() => setStep(2)}
              className="btn btn-outline"
            >
              Create Custom Alert
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              {selectedTemplate ? `Customize your ${selectedTemplate.title}` : 'Create Your Alert'}
            </h2>
            
            <div className="card p-6 space-y-6">
              {/* Restaurant Search */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Restaurant
                </label>
                <input
                  type="text"
                  placeholder="Search for a restaurant..."
                  value={alertData.restaurant}
                  onChange={(e) => setAlertData(prev => ({ ...prev, restaurant: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                {selectedTemplate && (
                  <p className="text-sm text-gray-500 mt-1">
                    Suggested: {selectedTemplate.description}
                  </p>
                )}
              </div>

              {/* Date and Time */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date
                  </label>
                  <input
                    type="date"
                    value={alertData.date}
                    onChange={(e) => setAlertData(prev => ({ ...prev, date: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time
                  </label>
                  <input
                    type="time"
                    value={alertData.time}
                    onChange={(e) => setAlertData(prev => ({ ...prev, time: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>

              {/* Party Size */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Party Size
                </label>
                <select
                  value={alertData.partySize}
                  onChange={(e) => setAlertData(prev => ({ ...prev, partySize: parseInt(e.target.value) }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  {[1,2,3,4,5,6,7,8,9,10].map(size => (
                    <option key={size} value={size}>{size} {size === 1 ? 'person' : 'people'}</option>
                  ))}
                </select>
              </div>

              {/* Contact Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    value={alertData.phone}
                    onChange={(e) => setAlertData(prev => ({ ...prev, phone: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    placeholder="your@email.com"
                    value={alertData.email}
                    onChange={(e) => setAlertData(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4 pt-4">
                <button
                  onClick={() => setStep(1)}
                  className="btn btn-ghost flex-1"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  className="btn btn-primary flex-1 flex items-center justify-center space-x-2"
                >
                  <span>Continue to Payment</span>
                  <ArrowRightIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Complete Your Purchase
            </h2>
            
            <div className="card p-6">
              {/* Alert Summary */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Alert Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Restaurant:</span>
                    <span className="font-medium">{alertData.restaurant || 'To be selected'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Date & Time:</span>
                    <span className="font-medium">{alertData.date} at {alertData.time}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Party Size:</span>
                    <span className="font-medium">{alertData.partySize} people</span>
                  </div>
                </div>
              </div>

              {/* Payment Info */}
              <div className="border-t pt-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-lg font-semibold">Single Alert</span>
                  <span className="text-2xl font-bold text-primary-600">$4.99</span>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircleIcon className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-blue-800">What you get:</span>
                  </div>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Instant notifications when your table opens</li>
                    <li>• AI-powered restaurant matching</li>
                    <li>• Faster monitoring (5-minute intervals)</li>
                    <li>• Email + SMS notifications</li>
                    <li>• Priority customer support</li>
                  </ul>
                </div>

                <button
                  onClick={handleQuickCreate}
                  disabled={isProcessing}
                  className="w-full btn btn-primary btn-lg flex items-center justify-center space-x-2"
                >
                  {isProcessing ? (
                    <>
                      <div className="loading-spinner w-5 h-5" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <CreditCardIcon className="w-5 h-5" />
                      <span>Pay $4.99 & Create Alert</span>
                    </>
                  )}
                </button>
                
                <p className="text-xs text-gray-500 text-center mt-4">
                  Secure payment powered by Stripe • No subscription required
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
