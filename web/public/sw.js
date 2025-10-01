/**
 * MouseAlerts Service Worker
 * 
 * This service worker provides:
 * - Offline caching for core app functionality
 * - Background sync for alert monitoring
 * - Push notification handling
 * - App installation prompts
 * - Network status management
 * 
 * Version: 1.0.0
 */

const CACHE_NAME = 'mousealerts-v1.0.0';
const OFFLINE_CACHE = 'mousealerts-offline-v1.0.0';

// Core app files to cache
const CORE_FILES = [
  '/',
  '/dashboard',
  '/alerts',
  '/alerts/create',
  '/quick-alert',
  '/billing',
  '/ai-prompt',
  '/auth/login',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  '/api/alerts',
  '/api/billing/current',
  '/api/alerts/plan-info'
];

// Static assets to cache
const STATIC_ASSETS = [
  '/_next/static/',
  '/favicon.ico',
  '/apple-touch-icon.png'
];

// Install event - cache core files
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching core files');
        return cache.addAll(CORE_FILES);
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== OFFLINE_CACHE) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle requests with caching strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (isCoreAppFile(url.pathname)) {
    event.respondWith(handleCoreAppFile(request));
  } else if (isAPIRequest(url.pathname)) {
    event.respondWith(handleAPIRequest(request));
  } else if (isStaticAsset(url.pathname)) {
    event.respondWith(handleStaticAsset(request));
  } else {
    event.respondWith(handleOtherRequest(request));
  }
});

// Handle core app files (pages, manifest, icons)
async function handleCoreAppFile(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful responses
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache', request.url);
    
    // Fall back to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // If it's a page request, return offline page
    if (request.destination === 'document') {
      return caches.match('/offline');
    }
    
    throw error;
  }
}

// Handle API requests with network-first strategy
async function handleAPIRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful API responses
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('API response not ok');
  } catch (error) {
    console.log('Service Worker: API network failed, trying cache', request.url);
    
    // Fall back to cache for API requests
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for API requests
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'This feature requires an internet connection' 
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  try {
    // Try cache first for static assets
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // If not in cache, fetch from network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache the response
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Static asset failed', request.url);
    throw error;
  }
}

// Handle other requests
async function handleOtherRequest(request) {
  try {
    return await fetch(request);
  } catch (error) {
    console.log('Service Worker: Request failed', request.url);
    throw error;
  }
}

// Helper functions to categorize requests
function isCoreAppFile(pathname) {
  return CORE_FILES.includes(pathname) || 
         pathname === '/' || 
         pathname.startsWith('/dashboard') ||
         pathname.startsWith('/alerts') ||
         pathname.startsWith('/billing') ||
         pathname.startsWith('/ai-prompt') ||
         pathname.startsWith('/quick-alert');
}

function isAPIRequest(pathname) {
  return pathname.startsWith('/api/');
}

function isStaticAsset(pathname) {
  return pathname.startsWith('/_next/static/') ||
         pathname.startsWith('/icons/') ||
         pathname.startsWith('/favicon') ||
         pathname.startsWith('/apple-touch-icon');
}

// Background sync for alert monitoring
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered', event.tag);
  
  if (event.tag === 'alert-monitoring') {
    event.waitUntil(handleAlertMonitoringSync());
  }
});

// Handle alert monitoring background sync
async function handleAlertMonitoringSync() {
  try {
    console.log('Service Worker: Checking alerts in background');
    
    // Get stored alerts from IndexedDB
    const alerts = await getStoredAlerts();
    
    if (alerts.length === 0) {
      return;
    }
    
    // Check each alert for availability
    for (const alert of alerts) {
      try {
        const response = await fetch(`/api/alerts/${alert.id}/check`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${alert.userToken}`
          }
        });
        
        if (response.ok) {
          const result = await response.json();
          if (result.available) {
            // Send push notification
            await sendPushNotification({
              title: '🎉 Reservation Available!',
              body: `${alert.restaurant} has availability for ${alert.date}`,
              icon: '/icons/icon-192x192.png',
              badge: '/icons/icon-72x72.png',
              data: {
                alertId: alert.id,
                restaurant: alert.restaurant,
                date: alert.date
              }
            });
          }
        }
      } catch (error) {
        console.error('Service Worker: Alert check failed', error);
      }
    }
  } catch (error) {
    console.error('Service Worker: Background sync failed', error);
  }
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received');
  
  let notificationData = {
    title: 'MouseAlerts',
    body: 'You have a new notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    data: {}
  };
  
  if (event.data) {
    try {
      notificationData = { ...notificationData, ...event.data.json() };
    } catch (error) {
      console.error('Service Worker: Failed to parse push data', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, {
      body: notificationData.body,
      icon: notificationData.icon,
      badge: notificationData.badge,
      data: notificationData.data,
      actions: [
        {
          action: 'view',
          title: 'View Alert',
          icon: '/icons/icon-192x192.png'
        },
        {
          action: 'dismiss',
          title: 'Dismiss',
          icon: '/icons/icon-192x192.png'
        }
      ],
      requireInteraction: true,
      tag: 'mousealerts-notification'
    })
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked', event.action);
  
  event.notification.close();
  
  if (event.action === 'view') {
    // Open the app to the relevant page
    event.waitUntil(
      clients.openWindow('/alerts')
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    return;
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
  console.log('Service Worker: Message received', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_ALERTS') {
    cacheAlerts(event.data.alerts);
  }
  
  if (event.data && event.data.type === 'REGISTER_PUSH') {
    registerPushSubscription(event.data.subscription);
  }
});

// Helper functions
async function getStoredAlerts() {
  // This would typically use IndexedDB
  // For now, return empty array
  return [];
}

async function cacheAlerts(alerts) {
  try {
    const cache = await caches.open(CACHE_NAME);
    await cache.put('/api/alerts', new Response(JSON.stringify(alerts)));
  } catch (error) {
    console.error('Service Worker: Failed to cache alerts', error);
  }
}

async function registerPushSubscription(subscription) {
  try {
    const response = await fetch('/api/notifications/subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(subscription)
    });
    
    if (response.ok) {
      console.log('Service Worker: Push subscription registered');
    }
  } catch (error) {
    console.error('Service Worker: Failed to register push subscription', error);
  }
}

async function sendPushNotification(notification) {
  try {
    const response = await fetch('/api/notifications/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(notification)
    });
    
    if (response.ok) {
      console.log('Service Worker: Push notification sent');
    }
  } catch (error) {
    console.error('Service Worker: Failed to send push notification', error);
  }
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'alert-monitoring') {
    event.waitUntil(handleAlertMonitoringSync());
  }
});

console.log('Service Worker: Loaded successfully');
