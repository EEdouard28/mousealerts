# 🐭 MouseAlerts – Build Spec

MouseAlerts is a mobile-first web application (PWA) that sends instant alerts when Disney dining reservations become available.  
This README describes the technical requirements, stack, and build roadmap.

---

## 🚀 **LIVE DEMO - Try It Now!**

**For Business Partners & Non-Technical Users:**

### 🌐 **Access the Live Demo**
**URL:** https://web-nu-six-61.vercel.app

### 📱 **How to Test the App (No Technical Knowledge Required)**

1. **Visit the website** - Click the link above
2. **Click "✨ Start Free Trial"** on the homepage
3. **Look for the yellow "🧪 Demo Mode" section** on the login page
4. **Click "🚀 Try Demo Account"** button
5. **Explore the full application:**
   - Dashboard with user interface
   - Create dining alerts with restaurant search
   - Test the AI Prompt Bar with natural language
   - View alert management features

### ✨ **What You'll See**
- **Professional landing page** with value proposition
- **User dashboard** with alert management
- **Restaurant search** with 100+ Disney restaurants
- **AI Prompt Bar** - Try typing "Princess dining Thursday at 7pm"
- **Mobile-responsive design** that works on phones and tablets

### 🎯 **Perfect for**
- Business partners reviewing the product
- Investors seeing the MVP
- User testing and feedback
- Stakeholder demonstrations

---

## 🛠️ Tech Stack

- **Frontend:** Next.js 14 (App Router, TypeScript, Tailwind, PWA support)
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL (SQLAlchemy + Alembic for migrations)
- **Cache/Queue:** Redis (for background workers and rate-limited tasks)
- **Background Jobs:** Celery (Python) or RQ
- **Notifications:**
  - Email: SendGrid/Postmark
  - SMS: Twilio
  - Push: Web Push API (VAPID)
- **Payments:** Stripe subscriptions
- **Auth:** Magic link (email) + JWT sessions

---

## 📂 Repo Structure

/api
/app
main.py
db.py
config.py
models/        # SQLAlchemy models
routers/       # FastAPI routes
services/      # business logic (alerts, notifications, AI parser)
workers/       # task queue consumers
/migrations
/web
app/             # Next.js App Router pages
components/
lib/             # API utilities
public/manifest.json
service-worker.js
/infra
docker-compose.yml
fly.toml (or render.yaml)
/tests
api/
e2e/

---

## 🔑 Core Data Models

**User**
- id, email, created_at, plan, subscription_status

**Alert**
- id, user_id, park, venue, date, time_start, time_end, party_size
- status (active/expired)
- channels (jsonb: push/email/sms)

**WatcherRun**
- id, venue, run_at, result_json, found_count, error

**Notification**
- id, alert_id, channel, status, sent_at, latency_ms

**Plan / Subscription**
- plan_id, name, limits (jsonb), price_cents
- subscription_id, user_id, plan_id, status, current_period_end

---

## 🚀 Development Roadmap

### Phase 0 – Foundation
- Scaffold FastAPI API with SQLAlchemy + Alembic migrations
- Set up Next.js 14 frontend with Tailwind
- Auth: magic link login (email only)
- Stripe test integration
- CI/CD config (GitHub Actions + Fly.io/Render deploy)

### Phase 1 – Core Alerts MVP
- Alert CRUD endpoints (`/alerts`)
- Worker + scheduler to poll Disney reservation endpoints (stub/mock first)
- De-dupe logic: same venue/date/time window notifies user only once per 24h
- Notifiers: email + SMS integration
- Frontend: alert creation form, alert list, run log (admin)

### Phase 2 – AI Prompt Bar
- `POST /nlu/parse` endpoint
- Date/time parsing (Chrono/Duckling)
- Embedding search for venues/tags
- LLM function-calling to produce structured JSON → alerts
- Frontend: Prompt bar with chips + “Create Alerts” suggestions

### Phase 3 – Premium & Payments
- Stripe subscription plans (Free, Premium, Family)
- Plan gates enforced (alerts per user, instant vs delayed notifications)
- Billing page + customer portal

### Phase 4 – PWA & Push
- Add PWA manifest + service worker
- Web Push (VAPID) notifications
- Notification preferences per alert

### Phase 5 – Admin & Monitoring
- Admin dashboard: active alerts, error rates, worker queue depth
- Metrics: slot_to_ping_seconds, duplicate rate, failed runs
- Sentry for error monitoring

---

## ✅ Acceptance Criteria

- Create alert → worker finds mock slot → user receives notification (email/SMS) in <10s median
- Duplicate prevention verified (no repeat notifications within 24h for same slot)
- AI Prompt Bar parses sample prompts with ≥80% accuracy
- Stripe plans update user limits within 60s after webhook
- PWA push notifications delivered successfully on iOS/Android + desktop Chrome

---

## 🧪 Testing

- Unit: de-dupe, retry/backoff logic, NLU parsing
- E2E: alert creation → simulated slot → notification received
- Load test: 10k concurrent alerts, queue latency within 60s

---

## 📊 Metrics to Track

- slot_to_ping_seconds (p50/p95)
- Alerts per active user
- Prompt → alert conversion rate
- Free → paid conversion
- Notification delivery success rate

---

## ⚖️ Notes

- MouseAlerts does not auto-book. It only notifies and deep-links to Disney’s official site/app.
- Brand/IP caution: avoid Disney logos/characters/fonts in the app.


