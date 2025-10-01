/**
 * Magic Link Verification Page
 * 
 * This page handles the verification of SMS magic link tokens.
 * Users are redirected here after clicking the magic link in their SMS.
 * 
 * Features:
 * - Automatic token extraction from URL parameters
 * - Token validation and user authentication
 * - Loading states and error handling
 * - Redirect to dashboard on successful verification
 * - Fallback manual token entry if needed
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircleIcon, ExclamationTriangleIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

export default function VerifyPage() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'manual'>('loading');
  const [error, setError] = useState('');
  const [manualToken, setManualToken] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (token) {
      verifyToken(token);
    } else {
      setStatus('manual');
    }
  }, [searchParams]);

  const verifyToken = async (token: string) => {
    try {
      const response = await fetch(`/api/auth/verify?token=${encodeURIComponent(token)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('success');
        toast.success('Welcome to MouseAlerts! 🎉');
        
        // Store auth token and redirect to dashboard
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
      } else {
        setError(data.detail || 'Invalid or expired token');
        setStatus('error');
        toast.error('Invalid or expired magic link');
      }
    } catch (error) {
      console.error('Verification error:', error);
      setError('Something went wrong. Please try again.');
      setStatus('error');
      toast.error('Verification failed');
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!manualToken.trim()) {
      toast.error('Please enter a token');
      return;
    }

    setIsSubmitting(true);
    await verifyToken(manualToken.trim());
    setIsSubmitting(false);
  };

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="card-glass p-8 text-center">
            <div className="loading-spinner mx-auto mb-6 w-8 h-8" />
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Verifying Your Magic Link...
            </h1>
            <p className="text-gray-600">
              Please wait while we verify your authentication
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="card-glass p-8 text-center">
            <div className="mb-6">
              <CheckCircleIcon className="w-12 h-12 text-green-500 mx-auto" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Success! 🎉
            </h1>
            
            <p className="text-gray-600 mb-6">
              You're now signed in to MouseAlerts. Redirecting to your dashboard...
            </p>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-700">
                <strong>Welcome aboard!</strong><br />
                You can now create Disney dining alerts and never miss a reservation again.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="card-glass p-8 text-center">
            <div className="mb-6">
              <ExclamationTriangleIcon className="w-12 h-12 text-red-500 mx-auto" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Verification Failed
            </h1>
            
            <p className="text-gray-600 mb-6">
              {error || 'Your magic link is invalid or has expired.'}
            </p>
            
            <div className="space-y-4">
              <button
                onClick={() => router.push('/auth/login')}
                className="btn btn-primary w-full"
              >
                Get New Magic Link
              </button>
              
              <button
                onClick={() => setStatus('manual')}
                className="btn btn-outline w-full"
              >
                Enter Token Manually
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Manual token entry
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="card-glass p-8">
          <div className="text-center mb-8">
            <div className="magic-glow mb-4">
              <SparklesIcon className="w-8 h-8 text-primary-500 mx-auto" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Enter Verification Token
            </h1>
            <p className="text-gray-600">
              If you have a verification token, enter it below
            </p>
          </div>

          <form onSubmit={handleManualSubmit} className="space-y-6">
            <div className="form-group">
              <label htmlFor="token" className="form-label">
                Verification Token
              </label>
              <input
                id="token"
                type="text"
                value={manualToken}
                onChange={(e) => setManualToken(e.target.value)}
                placeholder="Enter your verification token"
                className="form-input"
                required
              />
              <p className="form-help">
                This token was sent to you via SMS
              </p>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary w-full"
            >
              {isSubmitting ? (
                <>
                  <div className="loading-spinner mr-2" />
                  Verifying...
                </>
              ) : (
                'Verify Token'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => router.push('/auth/login')}
              className="text-primary-600 hover:text-primary-700 text-sm"
            >
              ← Back to Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
