/**
 * Offline Page
 * 
 * This page is displayed when users are offline and try to access
 * features that require an internet connection.
 * 
 * Features:
 * - Offline status indicator
 * - Cached content access
 * - Reconnection guidance
 * - Basic app functionality
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  WifiIcon, 
  ExclamationTriangleIcon,
  ArrowPathIcon,
  BellIcon,
  PlusIcon,
  CogIcon
} from '@heroicons/react/24/outline';

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const router = useRouter();

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check initial status
    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
    if (isOnline) {
      router.push('/dashboard');
    }
  };

  const handleGoToCachedContent = () => {
    router.push('/alerts');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Offline Status Card */}
        <div className="card text-center">
          <div className="card-body">
            {/* Status Icon */}
            <div className="flex justify-center mb-6">
              {isOnline ? (
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <WifiIcon className="w-8 h-8 text-green-600" />
                </div>
              ) : (
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
                </div>
              )}
            </div>

            {/* Status Message */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {isOnline ? 'Connection Restored!' : 'You\'re Offline'}
            </h1>
            
            <p className="text-gray-600 mb-6">
              {isOnline 
                ? 'Your internet connection has been restored. You can now access all features.'
                : 'It looks like you\'re not connected to the internet. Some features may not be available.'
              }
            </p>

            {/* Action Buttons */}
            <div className="space-y-3">
              {isOnline ? (
                <button
                  onClick={() => router.push('/dashboard')}
                  className="btn btn-primary w-full"
                >
                  <ArrowPathIcon className="w-5 h-5" />
                  Go to Dashboard
                </button>
              ) : (
                <>
                  <button
                    onClick={handleRetry}
                    className="btn btn-primary w-full"
                    disabled={retryCount > 3}
                  >
                    <ArrowPathIcon className="w-5 h-5" />
                    {retryCount > 3 ? 'Still Offline' : 'Try Again'}
                  </button>
                  
                  <button
                    onClick={handleGoToCachedContent}
                    className="btn btn-outline w-full"
                  >
                    <BellIcon className="w-5 h-5" />
                    View Cached Alerts
                  </button>
                </>
              )}
            </div>

            {/* Retry Counter */}
            {retryCount > 0 && (
              <p className="text-sm text-gray-500 mt-4">
                Retry attempts: {retryCount}
              </p>
            )}
          </div>
        </div>

        {/* Offline Features */}
        {!isOnline && (
          <div className="mt-6 space-y-4">
            {/* Available Offline Features */}
            <div className="card">
              <div className="card-body">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Available Offline
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <BellIcon className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-gray-700">View your alerts</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CogIcon className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-gray-700">App settings</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
                    <span className="text-sm text-gray-700">Create new alerts</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
                    <span className="text-sm text-gray-700">Real-time monitoring</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Connection Tips */}
            <div className="card card-gradient">
              <div className="card-body">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Connection Tips
                </h3>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>• Check your Wi-Fi or mobile data connection</li>
                  <li>• Try moving to a different location</li>
                  <li>• Restart your internet connection</li>
                  <li>• Check if other apps are working</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Online Features Reminder */}
        {isOnline && (
          <div className="mt-6">
            <div className="card card-gradient">
              <div className="card-body">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  🎉 You're Back Online!
                </h3>
                <p className="text-sm text-gray-700 mb-4">
                  All MouseAlerts features are now available:
                </p>
                <div className="space-y-2">
                  <div className="flex items-center space-x-3">
                    <BellIcon className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-gray-700">Real-time alert monitoring</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <PlusIcon className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-gray-700">Create new alerts</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <CogIcon className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-gray-700">Manage your account</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
