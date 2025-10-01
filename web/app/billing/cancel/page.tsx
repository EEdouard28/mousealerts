/**
 * Billing Cancel Page
 * 
 * This page is shown when users cancel the Stripe checkout process.
 * Users are redirected here if they cancel payment.
 * 
 * Features:
 * - Cancellation confirmation
 * - Option to try again
 * - Return to billing page
 */

'use client';

import { ArrowLeftIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';

export default function BillingCancelPage() {
  const router = useRouter();

  const handleTryAgain = () => {
    router.push('/billing');
  };

  const handleGoBack = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
      <div className="max-w-md mx-auto text-center">
        <div className="card p-8">
          <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Payment Cancelled
          </h1>
          
          <p className="text-gray-600 mb-6">
            No worries! You can always upgrade your plan later. Your current plan remains active.
          </p>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-800 mb-2">Need Help?</h3>
            <p className="text-sm text-blue-700">
              If you encountered any issues during checkout, please contact our support team.
            </p>
          </div>
          
          <div className="space-y-3">
            <button
              onClick={handleTryAgain}
              className="btn btn-primary w-full flex items-center justify-center space-x-2"
            >
              <span>Try Again</span>
              <ArrowRightIcon className="w-5 h-5" />
            </button>
            
            <button
              onClick={handleGoBack}
              className="btn btn-ghost w-full flex items-center justify-center space-x-2"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span>Back to Dashboard</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
