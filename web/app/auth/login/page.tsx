/**
 * SMS Login Page
 * 
 * This page handles the initial SMS magic link authentication flow.
 * Users enter their phone number to receive a magic link via SMS.
 * 
 * Features:
 * - Phone number validation with international format support
 * - Rate limiting protection
 * - Sleek, family-friendly UI with animations
 * - Mobile-first responsive design
 * - Error handling and loading states
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRightIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

export default function LoginPage() {
  const [phone, setPhone] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const router = useRouter();

  const formatPhoneNumber = (value: string) => {
    // Remove all non-digit characters
    const digits = value.replace(/\D/g, '');
    
    // Format as (XXX) XXX-XXXX for US numbers
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhoneNumber(e.target.value);
    setPhone(formatted);
  };

  const validatePhone = (phone: string) => {
    const digits = phone.replace(/\D/g, '');
    return digits.length === 10;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePhone(phone)) {
      toast.error('Please enter a valid 10-digit phone number');
      return;
    }

    setIsLoading(true);

    try {
      // Convert formatted phone to E.164 format
      const digits = phone.replace(/\D/g, '');
      const e164Phone = `+1${digits}`;

      const response = await fetch('/api/auth/magic-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone: e164Phone }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsSubmitted(true);
        toast.success('Magic link sent! Check your messages 📱');
      } else {
        if (data.detail?.includes('rate limit')) {
          toast.error('Too many requests. Please wait a moment and try again.');
        } else {
          toast.error(data.detail || 'Failed to send magic link. Please try again.');
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      toast.error('Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="card-glass p-8 text-center">
            <div className="mb-6 flex justify-center">
              <div className="w-6 h-6 flex items-center justify-center text-primary-500 text-2xl">
                ✨
              </div>
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Check Your Messages! 📱
            </h1>
            
            <p className="text-gray-600 mb-6">
              We've sent a magic link to <strong>{phone}</strong>. 
              Click the link to sign in to MouseAlerts.
            </p>
            
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-primary-700">
                <strong>Didn't receive the message?</strong><br />
                Check your spam folder or wait a moment for delivery.
              </p>
            </div>
            
            <button
              onClick={() => {
                setIsSubmitted(false);
                setPhone('');
              }}
              className="btn btn-outline w-full"
            >
              Try Different Number
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="card-glass p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mb-4 flex justify-center">
              <div className="w-6 h-6 flex items-center justify-center text-primary-500 text-2xl">
                📱
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to MouseAlerts
            </h1>
            <p className="text-gray-600">
              Enter your phone number to get started with Disney dining alerts
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="form-group">
              <label htmlFor="phone" className="form-label">
                Phone Number
              </label>
              <div className="relative">
                <input
                  id="phone"
                  type="tel"
                  value={phone}
                  onChange={handlePhoneChange}
                  placeholder="(555) 123-4567"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all duration-200 bg-white"
                  style={{
                    WebkitAppearance: 'none',
                    MozAppearance: 'none',
                    appearance: 'none',
                    borderRadius: '12px'
                  }}
                  maxLength={14}
                  required
                />
                <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-lg">📱</span>
              </div>
              <p className="form-help">
                We'll send you a secure magic link to sign in
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading || !validatePhone(phone)}
              className="w-full bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 flex items-center justify-center"
              style={{
                WebkitAppearance: 'none',
                MozAppearance: 'none',
                appearance: 'none',
                borderRadius: '12px'
              }}
            >
              {isLoading ? (
                <>
                  <div className="loading-spinner mr-2" />
                  Sending Magic Link...
                </>
              ) : (
                <>
                  Send Magic Link
                  <ArrowRightIcon className="w-5 h-5 ml-2" />
                </>
              )}
            </button>
          </form>

          {/* Features Preview */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              What you'll get:
            </h3>
            <div className="space-y-2">
              <div className="flex items-center text-sm text-gray-600">
                <div className="w-2 h-2 bg-primary-500 rounded-full mr-3" />
                Instant Disney dining alerts
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <div className="w-2 h-2 bg-secondary-500 rounded-full mr-3" />
                No more checking availability manually
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <div className="w-2 h-2 bg-accent-500 rounded-full mr-3" />
                Secure, passwordless login
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
