/**
 * Billing Success Page
 * 
 * This page is shown after successful Stripe checkout completion.
 * Users are redirected here from Stripe with success status.
 * 
 * Features:
 * - Success confirmation
 * - Plan upgrade confirmation
 * - Next steps guidance
 * - Redirect to dashboard
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircleIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

export default function BillingSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(true);
  const [paymentType, setPaymentType] = useState<string>('subscription');

  useEffect(() => {
    // Check if this is a single alert purchase
    const type = searchParams.get('type');
    setPaymentType(type || 'subscription');
    
    // Simulate processing the successful payment
    const timer = setTimeout(() => {
      setIsLoading(false);
      if (type === 'single') {
        toast.success('Single alert purchased! You can now create one premium alert.');
      } else {
        toast.success('Payment successful! Your plan has been upgraded.');
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [searchParams]);

  const handleContinue = () => {
    router.push('/dashboard');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4 w-8 h-8" />
          <p className="text-gray-600">Processing your payment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
      <div className="max-w-md mx-auto text-center">
        <div className="card p-8">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircleIcon className="w-8 h-8 text-green-600" />
          </div>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Payment Successful! 🎉
          </h1>
          
          <p className="text-gray-600 mb-6">
            {paymentType === 'single' 
              ? 'Your single alert purchase is complete! You can now create one premium alert.'
              : 'Your subscription has been activated. You now have access to all premium features.'
            }
          </p>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-green-800 mb-2">What's Next?</h3>
            <ul className="text-sm text-green-700 space-y-1">
              {paymentType === 'single' ? (
                <>
                  <li>• Create your single premium alert</li>
                  <li>• Access AI Prompt Bar for natural language setup</li>
                  <li>• Receive faster notifications (5min intervals)</li>
                  <li>• Priority customer support</li>
                </>
              ) : (
                <>
                  <li>• Create unlimited alerts (up to your plan limit)</li>
                  <li>• Access AI Prompt Bar for natural language alerts</li>
                  <li>• Receive faster notifications</li>
                  <li>• Priority customer support</li>
                </>
              )}
            </ul>
          </div>
          
          <button
            onClick={handleContinue}
            className="btn btn-primary w-full flex items-center justify-center space-x-2"
          >
            <span>Continue to Dashboard</span>
            <ArrowRightIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
