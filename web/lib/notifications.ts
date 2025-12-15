import React from 'react';

/**
 * Push Notification Service
 * 
 * This service handles push notification registration, subscription,
 * and management for MouseAlerts PWA.
 * 
 * Features:
 * - VAPID key management
 * - Push subscription handling
 * - Notification permission management
 * - Background sync support
 */

// Type declaration for Next.js environment variables
declare const process: {
  env: {
    NEXT_PUBLIC_VAPID_PUBLIC_KEY?: string;
  };
};

// Use native PushSubscription type

export interface NotificationPermission {
  granted: boolean;
  denied: boolean;
  default: boolean;
}

class NotificationService {
  private vapidPublicKey: string;
  private isSupported: boolean;

  constructor() {
    // Access Next.js environment variable - these are replaced at build time
    // Using type assertion since Next.js handles process.env replacement
    const env = typeof process !== 'undefined' ? (process as any).env : {};
    this.vapidPublicKey = env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '';
    this.isSupported = typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window;
  }

  /**
   * Check if push notifications are supported
   */
  isPushSupported(): boolean {
    return this.isSupported;
  }

  /**
   * Get current notification permission status
   */
  getPermissionStatus(): NotificationPermission {
    if (!this.isSupported) {
      return { granted: false, denied: true, default: false };
    }

    const permission = Notification.permission;
    return {
      granted: permission === 'granted',
      denied: permission === 'denied',
      default: permission === 'default'
    };
  }

  /**
   * Request notification permission
   */
  async requestPermission(): Promise<boolean> {
    if (!this.isSupported) {
      throw new Error('Push notifications are not supported');
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  /**
   * Register for push notifications
   */
  async subscribe(): Promise<PushSubscription | null> {
    if (!this.isSupported) {
      throw new Error('Push notifications are not supported');
    }

    try {
      // Register service worker
      const registration = await navigator.serviceWorker.register('/sw.js');
      await navigator.serviceWorker.ready;

      // Subscribe to push notifications
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: new Uint8Array(this.urlBase64ToUint8Array(this.vapidPublicKey))
      });

      // Send subscription to server
      await this.sendSubscriptionToServer(subscription);

      return subscription;
    } catch (error) {
      console.error('Failed to subscribe to push notifications:', error);
      throw error;
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe(): Promise<boolean> {
    if (!this.isSupported) {
      return false;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        await subscription.unsubscribe();
        await this.removeSubscriptionFromServer(subscription);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Failed to unsubscribe from push notifications:', error);
      return false;
    }
  }

  /**
   * Get current push subscription
   */
  async getSubscription(): Promise<PushSubscription | null> {
    if (!this.isSupported) {
      return null;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      return subscription;
    } catch (error) {
      console.error('Failed to get push subscription:', error);
      return null;
    }
  }

  /**
   * Send subscription to server
   */
  private async sendSubscriptionToServer(subscription: PushSubscription): Promise<void> {
    try {
      // Get auth token from localStorage
      const authToken = localStorage.getItem('auth_token');
      
      const response = await fetch('/api/notifications/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
        },
        body: JSON.stringify({
          endpoint: subscription.endpoint,
          keys: {
            p256dh: subscription.getKey ? (() => {
              const key = subscription.getKey('p256dh');
              return key ? Array.from(new Uint8Array(key)) : null;
            })() : null,
            auth: subscription.getKey ? (() => {
              const key = subscription.getKey('auth');
              return key ? Array.from(new Uint8Array(key)) : null;
            })() : null,
          }
        })
      });

      if (!response.ok) {
        throw new Error('Failed to register subscription with server');
      }
    } catch (error) {
      console.error('Failed to send subscription to server:', error);
      throw error;
    }
  }

  /**
   * Remove subscription from server
   */
  private async removeSubscriptionFromServer(subscription: PushSubscription): Promise<void> {
    try {
      // Get auth token from localStorage
      const authToken = localStorage.getItem('auth_token');
      
      const response = await fetch('/api/notifications/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
        }
      });

      if (!response.ok) {
        throw new Error('Failed to remove subscription from server');
      }
    } catch (error) {
      console.error('Failed to remove subscription from server:', error);
      throw error;
    }
  }

  /**
   * Convert VAPID key to Uint8Array
   */
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
}

// Export singleton instance
export const notificationService = new NotificationService();

// Export hook for React components
export function useNotifications() {
  const [permission, setPermission] = React.useState<NotificationPermission>(
    notificationService.getPermissionStatus()
  );
  const [isSubscribed, setIsSubscribed] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    // Check initial subscription status
    notificationService.getSubscription().then(subscription => {
      setIsSubscribed(!!subscription);
    });
  }, []);

  const requestPermission = async () => {
    setIsLoading(true);
    try {
      const granted = await notificationService.requestPermission();
      setPermission(notificationService.getPermissionStatus());
      return granted;
    } finally {
      setIsLoading(false);
    }
  };

  const subscribe = async () => {
    setIsLoading(true);
    try {
      const subscription = await notificationService.subscribe();
      setIsSubscribed(!!subscription);
      return subscription;
    } finally {
      setIsLoading(false);
    }
  };

  const unsubscribe = async () => {
    setIsLoading(true);
    try {
      const success = await notificationService.unsubscribe();
      setIsSubscribed(!success);
      return success;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    permission,
    isSubscribed,
    isLoading,
    requestPermission,
    subscribe,
    unsubscribe,
    isSupported: notificationService.isPushSupported()
  };
}
