# CLOUDFLARE FIREWALL RULES FOR MAXIMUM SECURITY
# These rules protect your site from bots, scrapers, and malicious actors

## MANUAL STEPS TO ADD IN CLOUDFLARE DASHBOARD:

### 1. Go to Cloudflare Dashboard
https://dash.cloudflare.com → Select "coachjvtech.us" → Security → WAF

### 2. Create Firewall Rules (Free Plan allows 5 rules)

---

### RULE 1: Block Known Bad Bots & Threat Actors
**Rule Name:** Block Threat Score > 10
**Expression:**
```
(cf.threat_score gt 10)
```
**Action:** Block
**Description:** Blocks visitors with high threat scores (known bad actors)

---

### RULE 2: Challenge Suspicious Countries (Optional - adjust to your needs)
**Rule Name:** Challenge High-Risk Countries  
**Expression:**
```
(ip.geoip.country in {"CN" "RU" "KP" "IR"})
```
**Action:** Managed Challenge
**Description:** Shows CAPTCHA to visitors from high-risk countries
**Note:** Remove or adjust countries as needed for your audience

---

### RULE 3: Rate Limit - Block Rapid Fire Requests
**Rule Name:** Rate Limit Protection
**Expression:**
```
(http.request.uri.path contains "/api/" or http.request.uri.path contains "/login" or http.request.uri.path contains "/admin")
```
**Action:** Challenge
**Description:** Challenges users making requests to sensitive endpoints
**Rate Limiting:** Enable "Rate Limiting" in Cloudflare dashboard separately

---

### RULE 4: Block Bad User Agents
**Rule Name:** Block Bot User Agents
**Expression:**
```
(http.user_agent contains "bot" and not http.user_agent contains "Googlebot" and not http.user_agent contains "Bingbot")
```
**Action:** Block
**Description:** Blocks most bots except legitimate search engines

---

### RULE 5: Protect Admin Panel
**Rule Name:** Admin Panel Protection
**Expression:**
```
(http.request.uri.path contains "/admin") and (cf.threat_score gt 5)
```
**Action:** Block
**Description:** Extra protection for admin panel - blocks any visitor with threat score > 5

---

## ADDITIONAL CLOUDFLARE SECURITY SETTINGS (Already Enabled via API):

✅ Security Level: HIGH
✅ Browser Integrity Check: ON
✅ Challenge Passage: 1 hour
✅ Bot Fight Mode: ON (if available)
✅ Always Use HTTPS: ON
✅ Automatic HTTPS Rewrites: ON
✅ TLS 1.3: ON
✅ Minimum TLS: 1.2
✅ Email Obfuscation: ON
✅ Hotlink Protection: ON
✅ HTTP/3: ON
✅ WebSockets: ON
✅ SSL Mode: Full (Strict)

---

## RATE LIMITING (Configure in Cloudflare):

Go to: Security → WAF → Rate limiting rules

### Rate Limit Rule 1: API Protection
- **Path:** Contains "/api/"
- **Requests:** 100 requests
- **Period:** 1 minute
- **Action:** Block for 10 minutes
- **Match:** Same IP + Same Path

### Rate Limit Rule 2: Login Protection  
- **Path:** Contains "/login" or "/auth"
- **Requests:** 5 requests
- **Period:** 5 minutes
- **Action:** Block for 15 minutes
- **Match:** Same IP

### Rate Limit Rule 3: Registration Protection
- **Path:** Contains "/register" or "/signup"
- **Requests:** 3 requests
- **Period:** 10 minutes
- **Action:** Block for 30 minutes
- **Match:** Same IP

---

## DDoS PROTECTION (Free - Auto-enabled)

✅ L3/L4 DDoS Protection: Automatic
✅ HTTP DDoS Protection: Automatic  
✅ Under Attack Mode: Available (manual toggle)

**To enable "Under Attack Mode" during an active attack:**
1. Go to Cloudflare Dashboard → Select your domain
2. Toggle "Under Attack Mode" in the Overview page
3. All visitors will see a challenge page for 5 seconds before accessing your site

---

## MANAGED RULES (Free Plan)

Go to: Security → WAF → Managed rules

Enable:
✅ Cloudflare OWASP Core Ruleset
✅ Cloudflare Managed Ruleset
✅ Cloudflare Exposed Credentials Check

---

## BOT MANAGEMENT (Paid Feature - Optional)

For advanced bot protection, upgrade to Pro plan ($20/month):
- Advanced bot detection
- JavaScript fingerprinting
- Machine learning-based detection
- Bot score analytics

---

## IP ACCESS RULES (Optional)

Go to: Security → WAF → Tools

### Whitelist Your IP (Optional):
- Add your personal IP address
- Action: Allow
- Zone: coachjvtech.us

### Blacklist Known Attackers:
- Add IPs from your logs that show malicious behavior
- Action: Block
- Zone: coachjvtech.us

---

## CLOUDFLARE ANALYTICS & MONITORING

Monitor your security:
1. **Security Analytics:** Security → Analytics
   - View blocked threats
   - See attack patterns
   - Monitor firewall events

2. **Security Events:** Security → Events
   - Real-time security log
   - Filter by action, IP, country
   - Investigate suspicious activity

3. **Bot Analytics:** Analytics → Traffic
   - Bot traffic vs human traffic
   - Bot sources and patterns

---

## ADDITIONAL RECOMMENDATIONS:

### 1. Enable Email Notifications
- Go to: Notifications
- Enable alerts for:
  - DDoS attacks
  - High threat traffic
  - SSL/TLS certificate issues
  - Firewall rule triggers

### 2. Enable Page Rules (3 free)
**Rule 1: Cache Everything (Performance)**
- URL: coachjvtech.us/static/*
- Cache Level: Cache Everything
- Edge Cache TTL: 1 month

**Rule 2: Disable Security for Webhooks**
- URL: coachjvtech.us/webhooks/*
- Security Level: Essentially Off
- (Only if you have payment webhooks that get blocked)

**Rule 3: Always Online**
- URL: coachjvtech.us/*
- Always Online: On

### 3. Setup Cloudflare Access (Zero Trust)
For admin panel protection:
- Go to: Zero Trust → Access → Applications
- Create application for /admin
- Require email authentication
- Add 2FA requirement

---

## MONITORING CHECKLIST

Daily:
□ Check Security Events for blocked attacks
□ Review Analytics for unusual traffic patterns
□ Monitor bot traffic percentages

Weekly:
□ Review firewall rule effectiveness
□ Check for new security advisories
□ Update rate limiting thresholds if needed

Monthly:
□ Audit firewall rules
□ Review and update IP blacklist
□ Check SSL certificate status
□ Review user access logs

---

## EMERGENCY PROCEDURES

### If Under Active Attack:
1. Enable "Under Attack Mode" immediately
2. Go to: Security → Settings → Enable "I'm Under Attack Mode"
3. This shows 5-second challenge to ALL visitors
4. Monitor Security Events to identify attack source
5. Create specific firewall rules to block attack vectors

### If Admin Panel is Compromised:
1. Immediately change admin password
2. Enable "Under Attack Mode"
3. Block all traffic to /admin except your IP
4. Check Django admin logs for unauthorized access
5. Review database for unauthorized changes
6. Update SECRET_KEY in Render environment variables

---

## CONTACT & SUPPORT

Cloudflare Support:
- Community: https://community.cloudflare.com
- Support Tickets: Dashboard → Help Center
- Status Page: https://www.cloudflarestatus.com

Django Security:
- Django Security Releases: https://www.djangoproject.com/weblog/
- Security Email: security@djangoproject.com

---

**Last Updated:** May 18, 2026
**Domain:** coachjvtech.us
**Platform:** Cloudflare Free Plan
