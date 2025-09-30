## ✨ What is MouseAlerts?

Disney dining reservations are competitive and stressful. Guests waste hours refreshing the site, only to miss the tables they want.  

**MouseAlerts fixes this.**  
- Get notified instantly when reservations open.  
- Create alerts in plain English with our **AI Prompt Bar** (“Princess dining Thursday at 7 pm in Magic Kingdom”).  
- Choose how you want notifications: push, text, or email.  
- Book directly in Disney’s official site/app (we don’t auto-book; you stay in control).  

---

## 🎯 Key Features

- **Instant Alerts** – Get notified the moment a reservation opens.  
- **Multiple Channels** – Push, SMS, and email options.  
- **AI Prompt Bar** – Type what you want, we build the alerts for you.  
- **Trip Profiles** – Set up your entire vacation in one flow.  
- **Smart Suggestions** – Alternatives and backup times when your first choice isn’t available.  
- **Transparency** – Clear “Why this alert?” explanations and success probability insights.  
- **Premium Options** – Unlimited alerts, priority notifications, expanded search.  

---

## 📅 Roadmap (High-Level)

- **Phase 0** – Foundation (repo, hosting, auth, CI/CD)  
- **Phase 1** – Core Alerts MVP (alerts → watch → notify → deep link)  
- **Phase 2** – AI Prompt Bar (plain-English setup, suggestions, upsells)  
- **Phase 3** – Premium & Payments (Stripe subscriptions, plan tiers)  
- **Phase 4** – Push-First PWA (installable, instant mobile notifications)  
- **Phase 5** – Beta Cohort (early adopters, feedback loop)  
- **Phase 6** – Public Launch (marketing site, support, PR)  

See the [[Wiki]](../../wiki) for detailed documentation.  

---

## 💼 Business Model

- Free plan: limited alerts, email only.  
- Single alert ($4.99): single alerts
- Premium ($9.99/mo): unlimited alerts, instant push, calendar sync.  
- Family/Pro ($19.99–$29.99/mo): multiple profiles, concierge recommendations.  
- Future expansion: Universal, cruises, and affiliate partnerships (dessert parties, hotels).  

---

## 🛠️ Tech Overview

- **Frontend:** Next.js (mobile-first PWA)  
- **Backend:** FastAPI (Python)  
- **Database:** Postgres + Redis (for workers/queues)  
- **Notifications:** Web-Push, SendGrid (email), Twilio (SMS)  
- **Payments:** Stripe subscriptions  

> Non-technical? Think of MouseAlerts as a **radar system**: it watches Disney’s dining site, finds openings, and pings you instantly with a booking link. You finish the reservation inside Disney’s official site or app.  

---

## 📊 Operations & Costs (MVP)

- Hosting (Fly.io/Render): $20–$50/mo  
- Database & Cache: $25–$50/mo  
- Notifications (email/SMS): $25–$50/mo  
- AI parsing: <$10/mo  
**Total:** ~$100–$150/month in early stage  

---

## ⚖️ Legal & Branding Notes

- MouseAlerts **notifies only** — it never auto-books or stores Disney credentials.  
- Users complete bookings directly on Disney’s site/app.  
- Name is descriptive; avoid Disney characters, logos, or fonts.  
- Trademark/IP review recommended before wide release.  

---

## 🤝 Contributing

We’re building MouseAlerts lean and fast.  
- Feedback? Open an [Issue](../../issues).  
- Want to help with code or testing? See the roadmap in the [[Wiki]](../../wiki).  

---

## 📬 Contact

For questions, ideas, or partnership inquiries, reach out to the maintainers.  