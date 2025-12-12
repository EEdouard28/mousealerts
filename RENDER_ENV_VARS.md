# Render Environment Variables Template

Copy these environment variables into your Render Web Service settings.

## Required Environment Variables

### Database (from your Render PostgreSQL service)
```
DATABASE_URL=postgresql://user:password@hostname:5432/dbname
```
**Note:** Use the **Internal Database URL** from your Render PostgreSQL dashboard.

### Redis (Optional - from your Render Redis service)
```
REDIS_URL=redis://hostname:6379
USE_REDIS=true
```
**Note:** Use the **Internal Redis URL** from your Render Redis dashboard. If you don't have Redis, set `USE_REDIS=false` and leave `REDIS_URL` empty.

### Authentication
```
JWT_SECRET=CHANGE_THIS_TO_A_SECURE_RANDOM_STRING_MIN_32_CHARACTERS
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

**To generate a secure JWT_SECRET, run this in your terminal:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### API Configuration
```
API_HOST=0.0.0.0
API_PORT=8000
APP_ENV=production
```

### CORS (Frontend URL)
```
ALLOWED_ORIGINS=https://web-nu-six-61.vercel.app,http://localhost:3000
ALLOWED_HOSTS=mousealerts-api.onrender.com,localhost
```
**Note:** Replace `mousealerts-api.onrender.com` with your actual Render service URL after deployment.

### Chrome/Chromium Paths (for web scraping)
```
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### Notifications (REQUIRED - Fill these in with your actual credentials)

#### SendGrid (Email)
```
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
```
**Get this from:** https://app.sendgrid.com/settings/api_keys

#### Twilio (SMS)
```
TWILIO_ACCOUNT_SID=ACyour_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_FROM_NUMBER=+15555555555
```
**Get these from:** https://console.twilio.com/

**Step-by-step guide to find Twilio credentials:**

1. **Go to Twilio Console:** https://console.twilio.com/
   - Log in with your Twilio account

2. **Find Account SID:**
   - On the main dashboard (home page), look at the top right or center
   - You'll see **"Account SID"** displayed prominently
   - It starts with `AC` followed by 32 characters
   - **Copy this value** → `TWILIO_ACCOUNT_SID`

3. **Find Auth Token:**
   - Still on the dashboard, look for **"Auth Token"**
   - Click the **eye icon** 👁️ or **"Show"** button to reveal it
   - It's a long string (32+ characters)
   - **Copy this value** → `TWILIO_AUTH_TOKEN`
   - ⚠️ **Important:** This is only shown once when you first create your account. If you can't see it, you may need to regenerate it:
     - Go to **Settings** → **General** → **Auth Tokens**
     - Click **"Create new token"** if needed

4. **Find Phone Number (FROM_NUMBER):**
   - In the left sidebar, click **"Phone Numbers"** → **"Manage"** → **"Active Numbers"**
   - You'll see a list of phone numbers you own
   - Click on the phone number you want to use
   - The phone number is displayed at the top (format: +1XXXXXXXXXX)
   - **Copy this value** → `TWILIO_FROM_NUMBER`
   - If you don't have a phone number yet:
     - Click **"Buy a number"** or **"Get a trial number"**
     - Select a number and purchase it (trial accounts get one free)

**Note:** Replace `+15555555555` with your actual Twilio phone number (format: +1XXXXXXXXXX)

**Quick Links:**
- Dashboard (Account SID visible): https://console.twilio.com/us1/develop/overview
- Phone Numbers: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
- Auth Tokens: https://console.twilio.com/us1/develop/runtime/api-keys

### Magic Link
```
MAGIC_LINK_BASE_URL=https://web-nu-six-61.vercel.app
```

### Optional: Monitoring
```
SENTRY_DSN=your_sentry_dsn_if_using
```
Leave empty if not using Sentry.

---

## Quick Setup Checklist

- [ ] Generate `JWT_SECRET` using the Python command above
- [ ] Get `SENDGRID_API_KEY` from SendGrid dashboard
- [ ] Get `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_NUMBER` from Twilio console
- [ ] Copy `DATABASE_URL` from Render PostgreSQL dashboard (Internal URL)
- [ ] Copy `REDIS_URL` from Render Redis dashboard (if using Redis)
- [ ] Update `ALLOWED_HOSTS` with your actual Render service URL after deployment

## After Deployment

Once your Render service is deployed, update:
- `ALLOWED_HOSTS` with your actual service URL (e.g., `your-app-name.onrender.com`)

