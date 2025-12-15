/**
 * Push Notification Subscription API Route
 * 
 * This route proxies push notification subscription requests to the backend API.
 * It handles the subscription data and forwards it to the FastAPI backend.
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const subscription = await request.json();
    const authToken = request.headers.get('authorization') || 
                      request.cookies.get('auth_token')?.value;

    if (!authToken) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Get the backend API URL from environment variable
    const apiBase = process.env.NEXT_PUBLIC_API_BASE;
    if (!apiBase) {
      return NextResponse.json(
        { error: 'API base URL not configured' },
        { status: 500 }
      );
    }

    // Forward the subscription to the backend
    const response = await fetch(`${apiBase}/api/push/subscribe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authToken,
      },
      body: JSON.stringify(subscription),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Failed to subscribe to push notifications:', error);
    return NextResponse.json(
      { error: 'Failed to subscribe to push notifications' },
      { status: 500 }
    );
  }
}

