# Deploy to Render in 5 Minutes - Step by Step

## What You'll Get
- **FREE hosting** (Render Free Tier)
- **Auto-deploy** from GitHub
- **SSL certificate** included
- Your domain: **coachjvtech.us**

## Step 1: Sign Up for Render (2 minutes)

1. Go to: **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"** (easiest)
4. Authorize Render to access your GitHub account

✅ **No credit card required for free tier!**

## Step 2: Create Web Service (3 minutes)

1. Once logged in, click the **"New +"** button (top right)
2. Select **"Web Service"**

3. **Connect Repository:**
   - You'll see a list of your GitHub repos
   - Find and click: **"KINGSACCOUNT1/coach-jv"**
   - Click **"Connect"**

4. **Render Auto-Detects Configuration:**
   - Render will find your `render.yaml` file
   - It will show: "Blueprint Spec Detected"
   - Click **"Apply"** or **"Create Web Service"**

5. **That's it!** Render will automatically:
   - Install Python 3.12.3
   - Install all dependencies from requirements.txt
   - Run collectstatic
   - Run database migrations
   - Create admin user
   - Start gunicorn server

## Step 3: Wait for Deployment (5-7 minutes)

Watch the logs as Render builds your app:
- Building... ⏳
- Deploying... ⏳
- **Live!** ✅

You'll get a URL like:
**https://coachjv-crypto.onrender.com**

## Step 4: Connect Your Domain (coachjvtech.us)

### In Render Dashboard:

1. Go to your web service
2. Click **"Settings"** tab (left sidebar)
3. Scroll down to **"Custom Domain"** section
4. Click **"+ Add Custom Domain"**
5. Enter: `coachjvtech.us`
6. Click **"Save"**
7. Repeat and add: `www.coachjvtech.us`

Render will show you DNS instructions.

### In Cloudflare:

1. Go to: **https://dash.cloudflare.com**
2. Select domain: **coachjvtech.us**
3. Go to **"DNS"** → **"Records"**

**Add these 2 records:**

**Record 1 - Root domain:**
- Type: `CNAME`
- Name: `@`
- Target: `coachjv-crypto.onrender.com` (your Render URL without https://)
- Proxy status: **Orange cloud ON (Proxied)** ☁️
- Click **"Save"**

**Record 2 - WWW subdomain:**
- Type: `CNAME`
- Name: `www`
- Target: `coachjv-crypto.onrender.com`
- Proxy status: **Orange cloud ON (Proxied)** ☁️
- Click **"Save"**

### Enable SSL in Cloudflare:

1. Go to **"SSL/TLS"** → **"Overview"**
2. Set to: **"Full (strict)"**
3. Go to **"SSL/TLS"** → **"Edge Certificates"**
4. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites

Wait **5-10 minutes** for DNS propagation.

## Step 5: Test Your Site! 🎉

Visit:
- **https://coachjvtech.us**
- **https://www.coachjvtech.us**

**Admin Panel:**
- URL: **https://coachjvtech.us/admin**
- Username: `admin`
- Password: `CryptoAdmin2026!`

## Important: Free Tier Limitations

Render Free Tier includes:
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ Free SSL
- ✅ Auto-deploy from GitHub
- ⚠️ **Spins down after 15 minutes of inactivity** (first request takes ~30 seconds to wake up)
- ⚠️ 750 hours/month (enough for testing)

**Upgrade to Paid ($7/month) for:**
- Always-on service (no spin down)
- More resources
- Better performance

## Monitoring & Logs

**View Logs:**
1. In Render dashboard, go to your service
2. Click **"Logs"** tab
3. See real-time logs

**Check Metrics:**
- Click **"Metrics"** tab
- See requests, CPU, memory usage

## Auto-Deploy

Every time you push to GitHub `main` branch:
- Render automatically rebuilds and redeploys
- Takes ~5 minutes
- Zero downtime deployment

To disable:
1. Settings → Build & Deploy
2. Toggle "Auto-Deploy" off

## Troubleshooting

**Site not loading:**
- Check logs in Render for errors
- Verify DNS records in Cloudflare
- Wait 10 minutes for DNS propagation

**Slow first load:**
- Normal on free tier (service spins down)
- First request takes ~30 seconds
- Upgrade to paid for always-on

**Static files missing:**
- Check Cloudinary configuration
- Verify collectstatic ran in build logs

**Database errors:**
- Check DATABASE_URL in environment variables
- Verify Neon PostgreSQL is accessible

## Cost Summary

| Service | Cost |
|---------|------|
| Render Free Tier | **$0/month** ✅ |
| Render Starter (Upgrade) | $7/month |
| Neon PostgreSQL | Free tier ✅ |
| Cloudinary | Free tier ✅ |
| Cloudflare | Free tier ✅ |

**Total: FREE** (with free tier limitations)

## Need Help?

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Support: support@render.com

---
**Ready to deploy?** Just follow Steps 1-2 above!

Your GitHub repo is ready: https://github.com/KINGSACCOUNT1/coach-jv
