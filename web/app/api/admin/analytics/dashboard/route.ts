/**
 * Mock Analytics Dashboard API
 * 
 * Provides mock analytics data for the admin dashboard.
 * In production, this would connect to the real FastAPI backend.
 */

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Mock analytics data
    const mockData = {
      revenue: {
        mrr: 1250.00,
        conversion_rate: 15.2,
        monthly_revenue: 3200.00,
        churn_rate: 2.1,
        total_users: 1250,
        paid_users: 190,
        active_subscriptions: 180
      },
      alerts: {
        total_alerts: 2450,
        active_alerts: 1890,
        paused_alerts: 320,
        expired_alerts: 240,
        success_rate: 94.5,
        recent_alerts: 156,
        run_success_rate: 98.2,
        avg_response_time: 1250
      },
      system: {
        api_status: "healthy",
        db_status: "healthy",
        error_rate: 0.8,
        last_success_time: new Date().toISOString(),
        pending_alerts: 45,
        uptime_percentage: 99.9
      }
    };

    return NextResponse.json(mockData);
  } catch (error) {
    console.error('Error fetching analytics:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analytics data' },
      { status: 500 }
    );
  }
}
