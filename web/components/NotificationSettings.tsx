/**
 * Notification Settings Component
 * 
 * This component allows users to manage their notification preferences
 * including push notifications, email notifications, and SMS alerts.
 * 
 * Features:
 * - Push notification toggle
 * - Email notification preferences
 * - SMS notification settings
 * - Notification timing controls
 * - Quiet hours configuration
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useNotifications } from '@/lib/notifications';
import { 
  BellIcon,
  BellSlashIcon,
  DevicePhoneMobileIcon,
  EnvelopeIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface NotificationPreferences {
  push: boolean;
  email: boolean;
  sms: boolean;
  instant: boolean;
  quietHours: {
    enabled: boolean;
    start: string;
    end: string;
  };
  alertTypes: {
    availability: boolean;
    reminders: boolean;
    updates: boolean;
  };
}

export default function NotificationSettings() {
  const { permission, isSubscribed, isLoading, requestPermission, subscribe, unsubscribe } = useNotifications();
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    push: false,
    email: true,
    sms: false,
    instant: false,
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00'
    },
    alertTypes: {
      availability: true,
      reminders: true,
      updates: false
    }
  });

  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Load saved preferences
    const saved = localStorage.getItem('notification-preferences');
    if (saved) {
      setPreferences(JSON.parse(saved));
    }
  }, []);

  const handlePreferenceChange = (key: keyof NotificationPreferences, value: any) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleNestedPreferenceChange = (parent: keyof NotificationPreferences, key: string, value: any) => {
    setPreferences(prev => ({
      ...prev,
      [parent]: {
        ...prev[parent] as any,
        [key]: value
      }
    }));
  };

  const handlePushToggle = async () => {
    if (!permission.granted) {
      const granted = await requestPermission();
      if (!granted) return;
    }

    if (isSubscribed) {
      await unsubscribe();
      handlePreferenceChange('push', false);
    } else {
      await subscribe();
      handlePreferenceChange('push', true);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage
      localStorage.setItem('notification-preferences', JSON.stringify(preferences));
      
      // Send to server
      await fetch('/api/notifications/preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences)
      });

      // Show success message
      // You could use a toast notification here
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Push Notifications */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-100 rounded-lg">
                <BellIcon className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Push Notifications</h3>
                <p className="text-sm text-gray-600">Get instant alerts on your device</p>
              </div>
            </div>
            
            <button
              onClick={handlePushToggle}
              disabled={isLoading || permission.denied}
              className={`btn ${isSubscribed ? 'btn-primary' : 'btn-outline'} btn-sm`}
            >
              {isLoading ? (
                <div className="loading-spinner w-4 h-4"></div>
              ) : isSubscribed ? (
                <>
                  <CheckCircleIcon className="w-4 h-4" />
                  Enabled
                </>
              ) : (
                <>
                  <BellSlashIcon className="w-4 h-4" />
                  Enable
                </>
              )}
            </button>
          </div>

          {permission.denied && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm text-red-700">
                Push notifications are blocked. Please enable them in your browser settings.
              </p>
            </div>
          )}

          {isSubscribed && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <p className="text-sm text-green-700">
                ✅ Push notifications are enabled and working!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Notification Types */}
      <div className="card">
        <div className="card-body">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Types</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <EnvelopeIcon className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">Email Notifications</p>
                  <p className="text-sm text-gray-600">Receive alerts via email</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.email}
                  onChange={(e) => handlePreferenceChange('email', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <DevicePhoneMobileIcon className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">SMS Notifications</p>
                  <p className="text-sm text-gray-600">Receive alerts via text message</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.sms}
                  onChange={(e) => handlePreferenceChange('sms', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Types */}
      <div className="card">
        <div className="card-body">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Alert Types</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Availability Alerts</p>
                <p className="text-sm text-gray-600">When reservations become available</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.alertTypes.availability}
                  onChange={(e) => handleNestedPreferenceChange('alertTypes', 'availability', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Reminder Alerts</p>
                <p className="text-sm text-gray-600">Before your dining reservations</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.alertTypes.reminders}
                  onChange={(e) => handleNestedPreferenceChange('alertTypes', 'reminders', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Update Alerts</p>
                <p className="text-sm text-gray-600">App updates and new features</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.alertTypes.updates}
                  onChange={(e) => handleNestedPreferenceChange('alertTypes', 'updates', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Quiet Hours */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <ClockIcon className="w-5 h-5 text-gray-600" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Quiet Hours</h3>
                <p className="text-sm text-gray-600">Pause notifications during specific times</p>
              </div>
            </div>
            
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={preferences.quietHours.enabled}
                onChange={(e) => handleNestedPreferenceChange('quietHours', 'enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          {preferences.quietHours.enabled && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Time
                </label>
                <input
                  type="time"
                  value={preferences.quietHours.start}
                  onChange={(e) => handleNestedPreferenceChange('quietHours', 'start', e.target.value)}
                  className="form-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Time
                </label>
                <input
                  type="time"
                  value={preferences.quietHours.end}
                  onChange={(e) => handleNestedPreferenceChange('quietHours', 'end', e.target.value)}
                  className="form-input w-full"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn btn-primary"
        >
          {isSaving ? (
            <>
              <div className="loading-spinner w-4 h-4"></div>
              Saving...
            </>
          ) : (
            'Save Preferences'
          )}
        </button>
      </div>
    </div>
  );
}
