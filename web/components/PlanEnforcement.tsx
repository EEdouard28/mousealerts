/**
 * Plan Enforcement Component
 * 
 * This component handles plan limit enforcement in the UI.
 * It shows upgrade prompts, plan limits, and disables features
 * based on the user's current subscription plan.
 * 
 * Features:
 * - Plan limit indicators
 * - Upgrade prompts
 * - Feature access control
 * - Usage statistics display
 */

'use client';

import React from 'react';
import { usePlan, useCanCreateAlert, useFeatureAccess, useUpgradeSuggestions } from '@/lib/plan';
import { 
  ExclamationTriangleIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ArrowRightIcon,
  StarIcon,
  BellIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { useRouter } from 'next/navigation';

interface PlanEnforcementProps {
  children: React.ReactNode;
  feature?: string;
  showUpgradePrompt?: boolean;
}

export default function PlanEnforcement({ 
  children, 
  feature, 
  showUpgradePrompt = true 
}: PlanEnforcementProps) {
  const { planInfo, usage, features, upgradeSuggestions } = usePlan();
  const { canCreateAlert } = useCanCreateAlert();
  const { canUseFeature } = useFeatureAccess();
  const router = useRouter();

  // Check if feature is restricted
  const isFeatureRestricted = feature && !canUseFeature(feature);
  const hasUpgradeSuggestions = upgradeSuggestions.length > 0;

  // If feature is restricted, show upgrade prompt
  if (isFeatureRestricted && showUpgradePrompt) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <div className="flex items-center space-x-3">
          <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-yellow-800">
              {feature === 'ai_prompt_bar' && 'AI Prompt Bar requires Premium'}
              {feature === 'sms_notifications' && 'SMS notifications require Premium'}
              {feature === 'instant_notifications' && 'Instant notifications require Premium'}
            </h3>
            <p className="text-sm text-yellow-700 mt-1">
              Upgrade to Premium to unlock this feature
            </p>
          </div>
          <button
            onClick={() => router.push('/billing')}
            className="btn btn-primary btn-sm"
          >
            Upgrade
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

// Component to show plan usage
export function PlanUsageDisplay() {
  const { usage, planInfo } = usePlan();

  if (!usage || !planInfo) return null;

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-900">Plan Usage</h3>
        <span className="text-xs text-gray-500">{planInfo.plan_name} Plan</span>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Active Alerts</span>
          <span className="text-sm font-medium">
            {usage.active_alerts} / {usage.unlimited ? '∞' : usage.max_alerts}
          </span>
        </div>
        
        {!usage.unlimited && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-500 h-2 rounded-full transition-all duration-300"
              style={{ 
                width: `${(usage.active_alerts / usage.max_alerts) * 100}%` 
              }}
            />
          </div>
        )}
        
        {usage.remaining <= 1 && !usage.unlimited && (
          <p className="text-xs text-amber-600">
            {usage.remaining === 0 ? 'Alert limit reached' : '1 alert remaining'}
          </p>
        )}
      </div>
    </div>
  );
}

// Component to show upgrade suggestions
export function UpgradeSuggestions() {
  const { upgradeSuggestions } = useUpgradeSuggestions();
  const router = useRouter();

  if (upgradeSuggestions.length === 0) return null;

  return (
    <div className="space-y-3">
      {upgradeSuggestions.map((suggestion, index) => (
        <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <StarIcon className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-blue-800">
                {suggestion.title}
              </h4>
              <p className="text-sm text-blue-700 mt-1">
                {suggestion.description}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Upgrade to {suggestion.upgrade_to}: {suggestion.benefit}
              </p>
            </div>
            <button
              onClick={() => router.push('/billing')}
              className="btn btn-primary btn-sm flex items-center space-x-1"
            >
              <span>Upgrade</span>
              <ArrowRightIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

// Component to show plan limits in alert creation
export function AlertLimitWarning() {
  const { canCreateAlert, usage } = useCanCreateAlert();
  const router = useRouter();

  if (canCreateAlert) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <div className="flex items-center space-x-3">
        <XCircleIcon className="w-6 h-6 text-red-600" />
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-red-800">
            Alert Limit Reached
          </h3>
          <p className="text-sm text-red-700 mt-1">
            You've used all {usage?.max_alerts} alerts on your {usage?.plan_name} plan.
            Upgrade to create more alerts.
          </p>
        </div>
        <button
          onClick={() => router.push('/billing')}
          className="btn btn-primary btn-sm"
        >
          Upgrade Plan
        </button>
      </div>
    </div>
  );
}

// Component to show feature access indicators
export function FeatureAccessIndicator({ feature, children }: { 
  feature: string; 
  children: React.ReactNode; 
}) {
  const { canUseFeature } = useFeatureAccess();
  const isEnabled = canUseFeature(feature);

  return (
    <div className={`${isEnabled ? '' : 'opacity-50 pointer-events-none'}`}>
      {children}
    </div>
  );
}
