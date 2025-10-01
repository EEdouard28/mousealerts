/**
 * PWA Installation Component
 * 
 * This component handles Progressive Web App installation prompts
 * and provides a native app-like experience for users.
 * 
 * Features:
 * - Install prompt detection
 * - Custom install button
 * - Installation status tracking
 * - App-like experience enhancements
 */

'use client';

import React, { useState, useEffect } from 'react';
import { 
  DevicePhoneMobileIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  CheckCircleIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export default function PWAInstall() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [installStatus, setInstallStatus] = useState<'idle' | 'installing' | 'installed' | 'dismissed'>('idle');

  useEffect(() => {
    // Check if app is already installed
    const checkInstallStatus = () => {
      if (window.matchMedia('(display-mode: standalone)').matches) {
        setIsInstalled(true);
        setInstallStatus('installed');
      }
    };

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowInstallPrompt(true);
    };

    // Listen for appinstalled event
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setInstallStatus('installed');
      setShowInstallPrompt(false);
      setDeferredPrompt(null);
    };

    // Check initial status
    checkInstallStatus();

    // Add event listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    setInstallStatus('installing');
    
    try {
      // Show the install prompt
      await deferredPrompt.prompt();
      
      // Wait for the user to respond
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        setInstallStatus('installed');
        setIsInstalled(true);
        setShowInstallPrompt(false);
      } else {
        setInstallStatus('dismissed');
        setShowInstallPrompt(false);
      }
      
      // Clear the deferred prompt
      setDeferredPrompt(null);
    } catch (error) {
      console.error('Installation failed:', error);
      setInstallStatus('idle');
    }
  };

  const handleDismiss = () => {
    setShowInstallPrompt(false);
    setInstallStatus('dismissed');
  };

  // Don't show if already installed or dismissed
  if (isInstalled || installStatus === 'dismissed') {
    return null;
  }

  // Don't show if no install prompt available
  if (!showInstallPrompt || !deferredPrompt) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-4 md:max-w-sm">
      <div className="card card-glass border-2 border-primary-200 shadow-xl">
        <div className="card-body">
          <div className="flex items-start space-x-3">
            {/* App Icon */}
            <div className="flex-shrink-0">
              <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-gray-900">
                Install MouseAlerts
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                Get instant notifications and a native app experience
              </p>
              
              {/* Benefits */}
              <div className="mt-2 space-y-1">
                <div className="flex items-center space-x-2 text-xs text-gray-600">
                  <CheckCircleIcon className="w-3 h-3 text-green-600" />
                  <span>Instant push notifications</span>
                </div>
                <div className="flex items-center space-x-2 text-xs text-gray-600">
                  <CheckCircleIcon className="w-3 h-3 text-green-600" />
                  <span>Works offline</span>
                </div>
                <div className="flex items-center space-x-2 text-xs text-gray-600">
                  <CheckCircleIcon className="w-3 h-3 text-green-600" />
                  <span>Home screen access</span>
                </div>
              </div>
            </div>

            {/* Close Button */}
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-2 mt-4">
            <button
              onClick={handleInstallClick}
              disabled={installStatus === 'installing'}
              className="btn btn-primary btn-sm flex-1"
            >
              {installStatus === 'installing' ? (
                <>
                  <div className="loading-spinner w-4 h-4"></div>
                  Installing...
                </>
              ) : (
                <>
                  <ArrowDownTrayIcon className="w-4 h-4" />
                  Install App
                </>
              )}
            </button>
            
            <button
              onClick={handleDismiss}
              className="btn btn-ghost btn-sm"
            >
              Maybe Later
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Hook for PWA installation
export function usePWAInstall() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [canInstall, setCanInstall] = useState(false);

  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setCanInstall(true);
    };

    const handleAppInstalled = () => {
      setIsInstalled(true);
      setCanInstall(false);
      setDeferredPrompt(null);
    };

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const install = async () => {
    if (!deferredPrompt) return false;

    try {
      await deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      setDeferredPrompt(null);
      return outcome === 'accepted';
    } catch (error) {
      console.error('Installation failed:', error);
      return false;
    }
  };

  return {
    canInstall,
    isInstalled,
    install
  };
}
