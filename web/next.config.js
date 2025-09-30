/**
 * MouseAlerts Web - Next.js Configuration
 * 
 * This configuration sets up Next.js 14 with:
 * - PWA support for mobile installation
 * - TypeScript and Tailwind CSS
 * - API proxy for development
 * - Service worker for offline functionality
 * - Image optimization for Disney restaurant photos
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: [
      'disneyworld.disney.go.com',
      'cdn1.parksmedia.wdpromedia.com',
      'secure.cdn1.wdpromedia.com'
    ],
    formats: ['image/webp', 'image/avif'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_BASE}/api/:path*`,
      },
    ]
  },
  async headers() {
    return [
      {
        source: '/manifest.json',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/service-worker.js',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=0, must-revalidate',
          },
        ],
      },
    ]
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }
    return config
  },
}

module.exports = nextConfig
