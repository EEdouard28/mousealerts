/**
 * Quick Alert Success Page
 * 
 * This page confirms the successful creation of a single alert
 * and provides next steps for the user.
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircleIcon, BellIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

export default function QuickAlertSuccessPage() {
  const router = useRouter();

  useEffect(() => {
    toast.success('Alert created successfully! You\'ll be notified when a table opens.');
  }, []);

  const handleViewDashboard = () => {
    router.push('/dashboard');
  };

  const handleCreateAnother = () => {
    router.push('/quick-alert');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
      <div className="max-w-md mx-auto text-center">
        <div className="card p-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircleIcon className="w-8 h-8 text-green-600" />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Alert Created! 🎉
          </h1>
          
          <p className="text-gray-600 mb-6">
            Your single alert is now active. We'll monitor Disney's dining availability and notify you the moment a table opens.
          </p>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2 mb-2">
              <BellIcon className="w-5 h-5 text-green-600" />
              <span className="font-semibold text-green-800">What happens next?</span>
            </div>
            <ul className="text-sm text-green-700 space-y-1 text-left">
              <li>• We'll check for availability every 5 minutes</li>
              <li>• You'll get instant email + SMS notifications</li>
              <li>• Click the link to book directly on Disney's site</li>
              <li>• Alert expires in 30 days or when you find a table</li>
            </ul>
          </div>
          
          <div className="space-y-3">
            <button
              onClick={handleViewDashboard}
              className="btn btn-primary w-full flex items-center justify-center space-x-2"
            >
              <span>View Dashboard</span>
              <ArrowRightIcon className="w-5 h-5" />
            </button>
            
            <button
              onClick={handleCreateAnother}
              className="btn btn-outline w-full"
            >
              Create Another Alert
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
