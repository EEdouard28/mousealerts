/**
 * MouseAlerts Web - Home Page
 * 
 * This is the main landing page that showcases:
 * - Hero section with value proposition
 * - Feature highlights
 * - Pricing information
 * - Call-to-action for sign up
 * - Mobile-first responsive design
 * - Automatic redirect for authenticated users
 */

'use client';

import { useAuth } from '@/lib/auth';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      router.push('/dashboard');
    }
  }, [user, isLoading, router]);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4 w-8 h-8" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't show landing page if user is authenticated
  if (user) {
    return null;
  }
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-accent-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="container-mobile sm:container-tablet lg:container-desktop py-12 sm:py-16 lg:py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold text-gray-900 mb-6">
              Never Miss Your
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-accent-600 block magic-sparkle">
                Dream Disney Dining
              </span>
            </h1>
            
            <p className="text-lg sm:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Get instant alerts when Disney dining reservations become available. 
              Stop refreshing and start enjoying your vacation planning.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <a href="/auth/login" className="btn-primary btn-xl magic-glow">
                ✨ Start Free Trial
              </a>
              <a href="/quick-alert" className="btn-accent btn-xl">
                ⚡ Quick Alert - $4.99
              </a>
              <button className="btn-ghost btn-xl">
                🎬 Watch Demo
              </button>
            </div>
            
            {/* Hero Stats */}
            <div className="grid grid-cols-3 gap-8 max-w-md mx-auto">
              <div className="text-center card-gradient p-4">
                <div className="text-2xl font-bold text-primary-600">10k+</div>
                <div className="text-sm text-gray-600 font-medium">Happy Families</div>
              </div>
              <div className="text-center card-gradient p-4" style={{animationDelay: '0.5s'}}>
                <div className="text-2xl font-bold text-secondary-600">50k+</div>
                <div className="text-sm text-gray-600 font-medium">Reservations Found</div>
              </div>
              <div className="text-center card-gradient p-4" style={{animationDelay: '1s'}}>
                <div className="text-2xl font-bold text-accent-600">95%</div>
                <div className="text-sm text-gray-600 font-medium">Success Rate</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 sm:py-20 lg:py-24 bg-gradient-to-b from-white to-gray-50">
        <div className="container-mobile sm:container-tablet lg:container-desktop">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-gray-900 mb-4">
              Why Choose <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-accent-600">MouseAlerts</span>?
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              We make Disney dining reservation hunting effortless with smart technology 
              and instant notifications. Perfect for busy families and Disney enthusiasts! 🎉
            </p>
          </div>
          
          {/* Feature Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="card-gradient p-6 text-center magic-sparkle">
              <div className="w-12 h-12 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">⚡ Instant Alerts</h3>
              <p className="text-gray-600">Get notified the moment reservations open up</p>
            </div>
            <div className="card-gradient p-6 text-center magic-sparkle" style={{animationDelay: '0.2s'}}>
              <div className="w-12 h-12 bg-secondary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">🤖 AI Prompt Bar</h3>
              <p className="text-gray-600">Describe what you want in plain English</p>
            </div>
            <div className="card-gradient p-6 text-center magic-sparkle" style={{animationDelay: '0.4s'}}>
              <div className="w-12 h-12 bg-accent-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📱</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">📱 Multiple Channels</h3>
              <p className="text-gray-600">Push, email, and SMS notifications</p>
            </div>
            <div className="card-gradient p-6 text-center magic-sparkle" style={{animationDelay: '0.6s'}}>
              <div className="w-12 h-12 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🚀</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">🚀 Quick Alert</h3>
              <p className="text-gray-600">One-time $4.99 payment, no subscription needed</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 sm:py-20 lg:py-24 bg-gradient-to-br from-gray-50 via-white to-primary-50">
        <div className="container-mobile sm:container-tablet lg:container-desktop">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-gray-900 mb-4">
              How It Works ✨
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get started in minutes and never miss a reservation again. 
              It's as easy as 1-2-3! 🎯
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center card-gradient magic-sparkle p-6">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-100 to-primary-200 rounded-3xl flex items-center justify-center mx-auto mb-6 magic-glow">
                <span className="text-3xl">🎯</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                🎯 Set Your Alerts
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Tell us what you're looking for using our AI Prompt Bar or 
                traditional form. We'll watch for availability 24/7!
              </p>
            </div>
            
            <div className="text-center card-gradient magic-sparkle p-6" style={{animationDelay: '0.3s'}}>
              <div className="w-20 h-20 bg-gradient-to-br from-secondary-100 to-secondary-200 rounded-3xl flex items-center justify-center mx-auto mb-6 magic-glow">
                <span className="text-3xl">⚡</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                ⚡ Get Instant Notifications
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Receive push notifications, emails, or SMS the moment 
                your desired reservation becomes available!
              </p>
            </div>
            
            <div className="text-center card-gradient magic-sparkle p-6" style={{animationDelay: '0.6s'}}>
              <div className="w-20 h-20 bg-gradient-to-br from-accent-100 to-accent-200 rounded-3xl flex items-center justify-center mx-auto mb-6 magic-glow">
                <span className="text-3xl">🎉</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                🎉 Book Immediately
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Click the notification to go directly to Disney's booking 
                page and secure your reservation!
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-16 sm:py-20 lg:py-24 bg-gradient-to-br from-gray-50 to-white">
        <div className="container-mobile sm:container-tablet lg:container-desktop">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing 💰
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Choose the plan that works for your family. No hidden fees, no surprises!
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="card-gradient p-8 text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Free</h3>
              <div className="text-4xl font-bold text-primary-600 mb-4">$0</div>
              <ul className="space-y-3 text-gray-600 mb-8">
                <li>✅ 2 active alerts</li>
                <li>✅ Email notifications</li>
                <li>✅ Basic support</li>
              </ul>
              <button className="btn-outline w-full">Get Started</button>
            </div>
            
            <div className="card-gradient p-8 text-center border-2 border-primary-500 relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-semibold">Most Popular</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Premium</h3>
              <div className="text-4xl font-bold text-primary-600 mb-4">$9.99<span className="text-lg text-gray-500">/mo</span></div>
              <ul className="space-y-3 text-gray-600 mb-8">
                <li>✅ Unlimited alerts</li>
                <li>✅ Push notifications</li>
                <li>✅ AI Prompt Bar</li>
                <li>✅ Priority support</li>
              </ul>
              <button className="btn-primary w-full">Start Free Trial</button>
            </div>
            
            <div className="card-gradient p-8 text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Family</h3>
              <div className="text-4xl font-bold text-primary-600 mb-4">$19.99<span className="text-lg text-gray-500">/mo</span></div>
              <ul className="space-y-3 text-gray-600 mb-8">
                <li>✅ Everything in Premium</li>
                <li>✅ Multiple profiles</li>
                <li>✅ Concierge recommendations</li>
                <li>✅ Priority booking</li>
              </ul>
              <button className="btn-outline w-full">Start Free Trial</button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-20 lg:py-24 bg-gradient-to-br from-primary-500 to-accent-500 text-white">
        <div className="container-mobile sm:container-tablet lg:container-desktop text-center">
          <h2 className="text-3xl sm:text-4xl font-display font-bold mb-4">
            Ready to Never Miss Your Dream Dining? 🎉
          </h2>
          <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
            Join thousands of families who never miss their favorite Disney restaurants. 
            Start your free trial today!
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="btn-secondary btn-xl">
              ✨ Start Free Trial
            </button>
            <button className="btn-ghost btn-xl text-white border-white hover:bg-white hover:text-primary-600">
              📞 Contact Sales
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}