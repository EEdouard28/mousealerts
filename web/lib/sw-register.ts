/**
 * Service Worker Registration
 * 
 * This module handles service worker registration and updates
 * for the MouseAlerts PWA.
 * 
 * Features:
 * - Automatic service worker registration
 * - Update notifications
 * - Background sync setup
 * - Push notification registration
 */

'use client';

import React from 'react';
import { notificationService } from './notifications';

class ServiceWorkerManager {
  private registration: ServiceWorkerRegistration | null = null;
  private updateAvailable = false;

  /**
   * Register the service worker
   */
  async register(): Promise<ServiceWorkerRegistration | null> {
    if (!('serviceWorker' in navigator)) {
      console.log('Service Worker not supported');
      return null;
    }

    try {
      this.registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      });

      console.log('Service Worker registered successfully');

      // Listen for updates
      this.registration.addEventListener('updatefound', () => {
        const newWorker = this.registration?.installing;
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.updateAvailable = true;
              this.notifyUpdateAvailable();
            }
          });
        }
      });

      // Handle controller change
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
      });

      return this.registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return null;
    }
  }

  /**
   * Check for service worker updates
   */
  async checkForUpdates(): Promise<boolean> {
    if (!this.registration) {
      return false;
    }

    try {
      await this.registration.update();
      return this.updateAvailable;
    } catch (error) {
      console.error('Failed to check for updates:', error);
      return false;
    }
  }

  /**
   * Apply service worker update
   */
  async applyUpdate(): Promise<void> {
    if (!this.registration || !this.updateAvailable) {
      return;
    }

    try {
      const newWorker = this.registration.waiting;
      if (newWorker) {
        newWorker.postMessage({ type: 'SKIP_WAITING' });
      }
    } catch (error) {
      console.error('Failed to apply update:', error);
    }
  }

  /**
   * Notify user about available update
   */
  private notifyUpdateAvailable(): void {
    // You can customize this notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('MouseAlerts Update Available', {
        body: 'A new version is available. Click to update.',
        icon: '/icons/icon-192x192.png',
        tag: 'update-available'
      });
    }

    // Dispatch custom event for UI components
    window.dispatchEvent(new CustomEvent('sw-update-available'));
  }

  /**
   * Setup background sync
   */
  async setupBackgroundSync(): Promise<void> {
    if (!this.registration) {
      return;
    }

    try {
      // Register for background sync
      await (this.registration as any).sync.register('alert-monitoring');
      console.log('Background sync registered');
    } catch (error) {
      console.error('Failed to register background sync:', error);
    }
  }

  /**
   * Setup push notifications
   */
  async setupPushNotifications(): Promise<void> {
    try {
      // Check if notifications are supported
      if (!notificationService.isPushSupported()) {
        console.log('Push notifications not supported');
        return;
      }

      // Request permission
      const permission = await notificationService.requestPermission();
      if (!permission) {
        console.log('Notification permission denied');
        return;
      }

      // Subscribe to push notifications
      const subscription = await notificationService.subscribe();
      if (subscription) {
        console.log('Push notifications enabled');
      }
    } catch (error) {
      console.error('Failed to setup push notifications:', error);
    }
  }

  /**
   * Get service worker status
   */
  getStatus(): {
    registered: boolean;
    updateAvailable: boolean;
    controller: ServiceWorker | null;
  } {
    return {
      registered: !!this.registration,
      updateAvailable: this.updateAvailable,
      controller: navigator.serviceWorker.controller
    };
  }
}

// Export singleton instance
export const swManager = new ServiceWorkerManager();

// Auto-register service worker on page load
if (typeof window !== 'undefined') {
  window.addEventListener('load', async () => {
    await swManager.register();
  });
}

// Export hook for React components
export function useServiceWorker() {
  const [status, setStatus] = React.useState(swManager.getStatus());
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    const handleUpdateAvailable = () => {
      setStatus(swManager.getStatus());
    };

    window.addEventListener('sw-update-available', handleUpdateAvailable);

    return () => {
      window.removeEventListener('sw-update-available', handleUpdateAvailable);
    };
  }, []);

  const checkForUpdates = async () => {
    setIsLoading(true);
    try {
      const hasUpdate = await swManager.checkForUpdates();
      setStatus(swManager.getStatus());
      return hasUpdate;
    } finally {
      setIsLoading(false);
    }
  };

  const applyUpdate = async () => {
    setIsLoading(true);
    try {
      await swManager.applyUpdate();
      setStatus(swManager.getStatus());
    } finally {
      setIsLoading(false);
    }
  };

  const setupBackgroundSync = async () => {
    setIsLoading(true);
    try {
      await swManager.setupBackgroundSync();
    } finally {
      setIsLoading(false);
    }
  };

  const setupPushNotifications = async () => {
    setIsLoading(true);
    try {
      await swManager.setupPushNotifications();
    } finally {
      setIsLoading(false);
    }
  };

  return {
    status,
    isLoading,
    checkForUpdates,
    applyUpdate,
    setupBackgroundSync,
    setupPushNotifications
  };
}
