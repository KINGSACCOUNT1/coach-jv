# DigitalOcean Deployment Guide for CoachJV Crypto Platform

## What You'll Need
- DigitalOcean account (sign up at https://www.digitalocean.com)
- GitHub repository: https://github.com/KINGSACCOUNT1/coach-jv
- Cloudflare domain: coachjvtech.us
- Cost: Starting at $5/month for Basic plan

## Step 1: Sign Up & Get Credits

1. Go to https://www.digitalocean.com
2. Sign up for a new account
3. **Get $200 free credit for 60 days** with this link: https://try.digitalocean.com/freetrialoffer/
4. Verify your account (requires credit card, but won't charge during trial)

## Step 2: Create App on DigitalOcean

### Option A: Using the Web Interface

1. **Log in to DigitalOcean**
2. Click **"Create"** → **"Apps"**
3. Select **"GitHub"** as source
4. Authorize DigitalOcean to access your GitHub
5. Select repository: **KINGSACCOUNT1/coach-jv**
6. Select branch: **main**
7. Click **"Next"**

### Configure Your App:

**Resources:**
- Type: Web Service
- Name: coachjv-crypto
- Environment: Python
- Build Command:
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- Run Command:
  ```bash
  python manage.py migrate && gunicorn cryptoplatform.wsgi:application --bind 0.0.0.0:$PORT
  ```
- HTTP Port: 8080

**Environment Variables** (Add these in the Environment tab):

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.12.3` |
| `DEBUG` | `False` |
| `SECRET_KEY` | `django-insecure-dev-key-change-in-production-please` (Mark as encrypted) |
| `ALLOWED_HOSTS` | `.ondigitalocean.app,coachjvtech.us,www.coachjvtech.us` |
| `DATABASE_URL` | `postgresql://neondb_owner:npg_NOnHIzUEV1T5@ep-curly-king-apo21r98-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require` (Mark as encrypted) |
| `CLOUDINARY_URL` | `cloudinary://688661857792261:LGe4IdMIbnhTE_4FYFgkwanf5Qo@dgo9rlph6` (Mark as encrypted) |
| `CLOUDINARY_CLOUD_NAME` | `dgo9rlph6` |
| `CLOUDINARY_API_KEY` | `688661857792261` |
| `CLOUDINARY_API_SECRET` | `LGe4IdMIbnhTE_4FYFgkwanf5Qo` (Mark as encrypted) |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_EMAIL` | `kingsleyotisi46@icloud.com` |
| `ADMIN_PASSWORD` | `CryptoAdmin2026!` (Mark as encrypted) |

**Plan:**
- Select: **Basic - $5/month** (or free trial)
- Instance: Basic XXS ($5/month)

8. Click **"Next"** → **"Review"**
9. Review settings and click **"Create Resources"**

### Option B: Using the Configuration File (Faster)

1. The `.do/app.yaml` file is ready in your project
2. In DigitalOcean, click **"Create"** → **"Apps"**
3. Select **"Import from a Spec"**
4. Paste the contents of `.do/app.yaml`
5. Click **"Next"** and complete the setup

## Step 3: Wait for Deployment

- DigitalOcean will automatically:
  - Clone your repository
  - Install dependencies
  - Run collectstatic
  - Run migrations
  - Start the server
- This takes **5-10 minutes**
- Watch the build logs for any errors

After deployment, you'll get a URL like:
`https://coachjv-crypto-xxxxx.ondigitalocean.app`

## Step 4: Connect Custom Domain (coachjvtech.us)

### In DigitalOcean:

1. Go to your App dashboard
2. Click **"Settings"** tab
3. Scroll to **"Domains"** section
4. Click **"Add Domain"**
5. Enter: `coachjvtech.us`
6. Click **"Add Domain"**
7. Also add: `www.coachjvtech.us`

DigitalOcean will show you:
- A CNAME record to add
- Or A records if using root domain

### In Cloudflare (DNS Setup):

1. Go to https://dash.cloudflare.com
2. Select domain: **coachjvtech.us**
3. Go to **"DNS"** → **"Records"**

**Add these DNS records:**

**For root domain:**
- Type: `CNAME`
- Name: `@`
- Target: `coachjv-crypto-xxxxx.ondigitalocean.app` (your DigitalOcean URL)
- Proxy status: **Orange cloud (Proxied)** ✅
- TTL: Auto

**For www subdomain:**
- Type: `CNAME`
- Name: `www`
- Target: `coachjv-crypto-xxxxx.ondigitalocean.app`
- Proxy status: **Orange cloud (Proxied)** ✅
- TTL: Auto

4. Click **"Save"**

### Configure SSL in Cloudflare:

1. Go to **"SSL/TLS"** → **"Overview"**
2. Set encryption mode to: **"Full (strict)"**
3. Go to **"SSL/TLS"** → **"Edge Certificates"**
4. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Minimum TLS Version: 1.2

5. Wait **5-15 minutes** for DNS propagation

## Step 5: Verify Deployment

**Test your site:**
- https://coachjvtech.us
- https://www.coachjvtech.us

**Access Admin Panel:**
- URL: https://coachjvtech.us/admin
- Username: `admin`
- Password: `CryptoAdmin2026!`

## Step 6: Enable Auto-Deploy (Optional)

In DigitalOcean App settings:
1. Go to **"Settings"** → **"App-Level Settings"**
2. Enable **"Autodeploy"**
3. Now every push to `main` branch will auto-deploy

## Monitoring & Logs

**View Logs:**
1. In DigitalOcean, go to your App
2. Click **"Runtime Logs"** tab
3. Monitor for errors

**Check Performance:**
1. Go to **"Insights"** tab
2. View request metrics, response times, errors

## Troubleshooting

### Site not loading:
- Check build logs in DigitalOcean
- Verify all environment variables are set
- Check DNS records in Cloudflare (orange cloud enabled)
- Wait 15 minutes for DNS propagation

### Static files not loading:
- Verify CLOUDINARY settings are correct
- Check collectstatic ran during build
- Look for errors in build logs

### Database errors:
- Verify DATABASE_URL is correct
- Check if migrations ran successfully
- View runtime logs for specific errors

### Domain not working:
- Ensure DNS records point to DigitalOcean app URL
- Verify SSL is "Full (strict)" in Cloudflare
- Check ALLOWED_HOSTS includes your domain
- Try disabling proxy (grey cloud) temporarily to test

## Costs

**DigitalOcean App Platform:**
- Basic (512 MB RAM, 1 vCPU): **$5/month**
- Professional (1 GB RAM, 1 vCPU): **$12/month**
- **Free $200 credit for 60 days** for new accounts

**External Services (Already configured):**
- Neon PostgreSQL: Free tier ✅
- Cloudinary: Free tier ✅
- Cloudflare: Free tier ✅

**Total estimated cost after free trial:** $5/month

## Scaling

To handle more traffic:
1. Go to App settings
2. Increase instance count (horizontal scaling)
3. Or upgrade to Professional plan (vertical scaling)

## Backup & Security

**Recommended:**
- Enable database backups in Neon
- Use environment variables for secrets (already done ✅)
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Enable Cloudflare WAF for DDoS protection

## Support

- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/
- Community: https://www.digitalocean.com/community
- Support: support@digitalocean.com

---
**Deployment Guide Created:** May 18, 2026  
**Domain:** coachjvtech.us  
**Platform:** DigitalOcean App Platform  
**Repository:** https://github.com/KINGSACCOUNT1/coach-jv
