# Deployment Guide for MouseAlerts

This guide covers how to deploy the MouseAlerts backend to Fly.io for the 1-week test.

## Prerequisites
- [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/) installed
- `flyctl auth login` completed

## 1. Prepare Backend for Fly.io

1. Navigate to the project root.
2. Create/Check `fly.toml` (if not present, run `fly launch` in `api/` folder or root).

Here is a recommended `fly.toml` configuration for the API:

```toml
app = "mousealerts-api"
primary_region = "iad"

[build]
  dockerfile = "infra/Dockerfile.api" 

[env]
  PORT = "8000"
  # Override chrome paths for Fly's linux environment
  CHROME_BIN = "/usr/bin/chromium"
  CHROMEDRIVER_PATH = "/usr/bin/chromedriver"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
```

## 2. Set Environment Variables

Set these production secrets on Fly.io:

```bash
# Database (Fly will likely attach Postgres automatically if you chose it during launch)
fly secrets set DATABASE_URL=postgresql://user:pass@hostname:5432/db

# Authentication
fly secrets set JWT_SECRET_KEY=your-secure-random-string
fly secrets set JWT_ALGORITHM=HS256

# Notifications (Required for alerts to actually reach you!)
fly secrets set SENDGRID_API_KEY=SG.xxxx
fly secrets set TWILIO_ACCOUNT_SID=ACxxxx
fly secrets set TWILIO_AUTH_TOKEN=xxxx
fly secrets set TWILIO_PHONE_NUMBER=+15555555555
```

## 3. Deploy

```bash
fly deploy
```

## 4. Manual Verification

Once deployed, verify the scraper works:

1. **Log in** to your deployed frontend (or use Postman against the API).
2. **Create an Alert** for a restaurant (e.g., "Be Our Guest Restaurant").
3. **Trigger Manual Check** (using your admin token):
   ```bash
   curl -X POST https://your-app.fly.dev/api/worker/check-alert/{alert_id} \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```
4. **Check Logs**:
   ```bash
   fly logs
   ```
   Look for:
   - "Using custom Chrome binary..."
   - "Resolved 'Be Our Guest Restaurant' to ID..."
   - "Alert monitoring completed..."

## Troubleshooting

- **"Restaurant not found"**: Check logs. Did the search-first logic find the ID?
- **"WebDriverException"**: Ensure Fly app has enough memory. You may need to scale up:
  ```bash
  fly scale memory 1024
  ```

