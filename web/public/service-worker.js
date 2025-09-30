/**
 * MouseAlerts Web - Service Worker
 * 
 * This service worker provides:
 * - Offline functionality for core features
 * - Push notification handling
 * - Background sync for alerts
 * - Caching strategies for performance
 * - PWA installation support
 */

const CACHE_NAME = 'mousealerts-v1'
const API_CACHE_NAME = 'mousealerts-api-v1'
const STATIC_CACHE_NAME = 'mousealerts-static-v1'

// Files to cache for offline functionality
const STATIC_FILES = [
  '/',
  '/alerts',
  '/alerts/new',
  '/prompt',
  '/manifest.json',
  '/offline.html'
]

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/health',
  '/api/alerts',
  '/api/plans'
]

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...')
  
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        return cache.addAll(STATIC_FILES)
      }),
      caches.open(API_CACHE_NAME).then((cache) => {
        return cache.addAll(API_ENDPOINTS.map(endpoint => `/api${endpoint}`))
      })
    ]).then(() => {
      console.log('Service Worker: Installation complete')
      return self.skipWaiting()
    })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...')
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && 
              cacheName !== API_CACHE_NAME && 
              cacheName !== STATIC_CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    }).then(() => {
      console.log('Service Worker: Activation complete')
      return self.clients.claim()
    })
  )
})

// Fetch event - handle requests with caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request))
    return
  }
  
  // Handle static file requests
  if (request.method === 'GET') {
    event.respondWith(handleStaticRequest(request))
    return
  }
})

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request)
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(API_CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache:', error)
    
    // Fall back to cache
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Return offline response for API requests
    return new Response(
      JSON.stringify({ 
        error: 'Offline', 
        message: 'You are offline. Some features may not be available.' 
      }),
      { 
        status: 503, 
        headers: { 'Content-Type': 'application/json' } 
      }
    )
  }
}

// Handle static file requests with cache-first strategy
async function handleStaticRequest(request) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }
    
    // Fall back to network
    const networkResponse = await fetch(request)
    
    // Cache successful responses
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    
    return networkResponse
  } catch (error) {
    console.log('Service Worker: Both cache and network failed:', error)
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/offline.html')
    }
    
    // Return generic offline response
    return new Response('Offline', { status: 503 })
  }
}

// Push event - handle push notifications
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push received:', event)
  
  if (event.data) {
    const data = event.data.json()
    const options = {
      body: data.body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      data: data.data,
      actions: [
        {
          action: 'book',
          title: 'Book Now',
          icon: '/icons/action-book.png'
        },
        {
          action: 'dismiss',
          title: 'Dismiss',
          icon: '/icons/action-dismiss.png'
        }
      ],
      requireInteraction: true,
      tag: data.tag || 'mousealerts-alert'
    }
    
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    )
  }
})

// Notification click event - handle notification interactions
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked:', event)
  
  event.notification.close()
  
  if (event.action === 'book' && event.notification.data?.booking_url) {
    // Open booking URL in new tab
    event.waitUntil(
      clients.openWindow(event.notification.data.booking_url)
    )
  } else if (event.action === 'dismiss') {
    // Just close the notification
    return
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((clientList) => {
        // If app is already open, focus it
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            return client.focus()
          }
        }
        // Otherwise open new window
        return clients.openWindow('/')
      })
    )
  }
})

// Background sync - handle offline actions
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync:', event.tag)
  
  if (event.tag === 'background-sync-alerts') {
    event.waitUntil(syncAlerts())
  }
})

// Sync alerts when back online
async function syncAlerts() {
  try {
    // Get pending alerts from IndexedDB
    const pendingAlerts = await getPendingAlerts()
    
    for (const alert of pendingAlerts) {
      try {
        await fetch('/api/alerts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(alert)
        })
        
        // Remove from pending queue
        await removePendingAlert(alert.id)
      } catch (error) {
        console.error('Service Worker: Failed to sync alert:', error)
      }
    }
  } catch (error) {
    console.error('Service Worker: Background sync failed:', error)
  }
}

// Helper functions for IndexedDB operations
async function getPendingAlerts() {
  // Implementation would use IndexedDB to get pending alerts
  return []
}

async function removePendingAlert(alertId) {
  // Implementation would use IndexedDB to remove pending alert
  return true
}

// Message event - handle messages from main thread
self.addEventListener('message', (event) => {
  console.log('Service Worker: Message received:', event.data)
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME })
  }
})
