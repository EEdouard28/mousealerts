/**
 * Protected Route Component
 * 
 * This component wraps pages that require authentication.
 * It redirects unauthenticated users to the login page.
 * 
 * Features:
 * - Automatic redirect for unauthenticated users
 * - Loading state while checking authentication
 * - Optional redirect path customization
 * - Seamless user experience
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export default function ProtectedRoute({ 
  children, 
  redirectTo = '/auth/login' 
}: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push(redirectTo);
    }
  }, [user, isLoading, router, redirectTo]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4 w-6 h-6" />
          <p className="text-gray-600">Loading...</p>
          <div className="mt-4">
            <button 
              onClick={(e) => {
                e.preventDefault();
                console.log('Button clicked - setting up mock user');
                
                // Set up mock user for testing
                const mockUser = {
                  id: 'mock-user-123',
                  phone: '+15551234567',
                  email: 'test@mousealerts.com',
                  plan: 'free',
                  created_at: new Date().toISOString(),
                };
                
                try {
                  localStorage.setItem('auth_token', 'mock-jwt-token-123');
                  localStorage.setItem('user', JSON.stringify(mockUser));
                  console.log('Mock user set up, reloading page...');
                  window.location.reload();
                } catch (error) {
                  console.error('Error setting up mock user:', error);
                }
              }}
              className="btn btn-primary btn-sm"
              style={{ cursor: 'pointer' }}
            >
              Set Up Mock User for Testing
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated
  if (!user) {
    return null;
  }

  return <>{children}</>;
}
