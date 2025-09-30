/**
 * MouseAlerts Web - Root Layout
 * 
 * This is the root layout component that wraps all pages.
 * It provides:
 * - Global styles and Tailwind CSS
 * - Authentication context
 * - Toast notifications
 * - PWA manifest and meta tags
 * - Mobile-first responsive design
 */

import type { Metadata } from 'next'
import { Inter, Poppins } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'
// import { AuthProvider } from '@/components/providers/AuthProvider'
// import { QueryProvider } from '@/components/providers/QueryProvider'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-poppins',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'MouseAlerts - Disney Dining Reservation Alerts',
  description: 'Get instant alerts when Disney dining reservations become available. Never miss your favorite restaurants again!',
  keywords: ['Disney', 'dining', 'reservations', 'alerts', 'Magic Kingdom', 'EPCOT', 'Hollywood Studios', 'Animal Kingdom'],
  authors: [{ name: 'MouseAlerts Team' }],
  creator: 'MouseAlerts',
  publisher: 'MouseAlerts',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'MouseAlerts - Disney Dining Reservation Alerts',
    description: 'Get instant alerts when Disney dining reservations become available. Never miss your favorite restaurants again!',
    siteName: 'MouseAlerts',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'MouseAlerts - Disney Dining Reservation Alerts',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'MouseAlerts - Disney Dining Reservation Alerts',
    description: 'Get instant alerts when Disney dining reservations become available. Never miss your favorite restaurants again!',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'MouseAlerts',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/favicon.ico" />
        <meta name="theme-color" content="#f2851a" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="MouseAlerts" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#f2851a" />
      </head>
      <body className="min-h-screen bg-gray-50 font-sans antialiased">
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#22c55e',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  )
}
