# Render Deployment Guide for CoachJV Crypto Platform

## Prerequisites
✅ GitHub repo: https://github.com/KINGSACCOUNT1/coach-jv
✅ Cloudflare account with domain: coachjvtech.us
✅ render.yaml configuration file ready

## Step 1: Deploy to Render

1. Go to https://render.com and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub account if not already connected
4. Select repository: `KINGSACCOUNT1/coach-jv`
5. Render will automatically detect `render.yaml` configuration
6. Click "Create Web Service"

Render will automatically:
- Install dependencies from requirements.txt
- Run collectstatic
- Run database migrations
- Create admin user
- Start gunicorn server

## Step 2: Get Your Render URL

After deployment completes, you'll get a URL like:
`https://coachjv-crypto.onrender.com`

## Step 3: Connect Custom Domain (coachjvtech.us)

### On Render:
1. Go to your web service dashboard
2. Click "Settings" tab
3. Scroll to "Custom Domain" section
4. Click "Add Custom Domain"
5. Enter: `coachjvtech.us`
6. Also add: `www.coachjvtech.us`
7. Render will show you DNS records to add

### On Cloudflare:
1. Go to https://dash.cloudflare.com
2. Select domain: `coachjvtech.us`
3. Go to "DNS" → "Records"
4. Add the following records:

**For root domain (coachjvtech.us):**
- Type: `CNAME`
- Name: `@`
- Target: `coachjv-crypto.onrender.com` (or the URL Render provides)
- Proxy status: Orange cloud (Proxied)

**For www subdomain:**
- Type: `CNAME`
- Name: `www`
- Target: `coachjv-crypto.onrender.com`
- Proxy status: Orange cloud (Proxied)

5. Click "Save"

### Enable SSL:
1. In Cloudflare, go to "SSL/TLS" → "Overview"
2. Set encryption mode to "Full (strict)"
3. Wait 5-10 minutes for SSL to propagate

## Step 4: Verify Deployment

Visit your site:
- https://coachjvtech.us
- https://www.coachjvtech.us

Admin panel:
- https://coachjvtech.us/admin
- Username: admin
- Password: CryptoAdmin2026!

## Environment Variables (Already configured in render.yaml)

✅ DATABASE_URL - Neon PostgreSQL
✅ CLOUDINARY - Media storage
✅ SECRET_KEY - Auto-generated
✅ ALLOWED_HOSTS - Includes coachjvtech.us
✅ DEBUG - Set to False for production

## Troubleshooting

**If site doesn't load:**
- Check Render logs for errors
- Verify DNS records in Cloudflare
- Ensure SSL is set to "Full (strict)"
- Wait 5-10 minutes for DNS propagation

**If admin panel doesn't work:**
- Check if migrations ran successfully in Render logs
- Verify create_admin management command executed

**If static files don't load:**
- Check Cloudinary configuration
- Verify collectstatic ran during build

## Next Steps

1. Test all features on production
2. Update email settings in .env if needed
3. Monitor Render logs for any errors
4. Set up monitoring/alerts in Render dashboard

## Support

- Render Docs: https://render.com/docs
- Cloudflare Docs: https://developers.cloudflare.com
- Django Docs: https://docs.djangoproject.com

---
Deployment configured on: May 18, 2026
Domain: coachjvtech.us
