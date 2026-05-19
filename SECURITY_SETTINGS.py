# COMPREHENSIVE SECURITY CONFIGURATION FOR DJANGO
# Add these settings to your cryptoplatform/settings.py file

# ============================================================================
# SECURITY HEADERS & SETTINGS
# ============================================================================

# HTTPS & SSL Settings
SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
CSRF_COOKIE_SECURE = True  # CSRF cookies only over HTTPS

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy (CSP)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_IMG_SRC = ("'self'", "data:", "https:", "http:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)  # Prevent clickjacking

# Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME sniffing
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filter
X_FRAME_OPTIONS = 'DENY'  # Prevent iframe embedding (clickjacking protection)
SECURE_REFERRER_POLICY = 'same-origin'  # Control referrer information

# ============================================================================
# SESSION & COOKIE SECURITY
# ============================================================================

SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour session timeout
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session on every request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_AGE = 31449600  # 1 year

# ============================================================================
# PASSWORD & AUTH SECURITY
# ============================================================================

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,  # Require at least 10 characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Failed login attempt tracking (requires django-axes or similar)
# AXES_FAILURE_LIMIT = 5  # Lock account after 5 failed attempts
# AXES_COOLOFF_TIME = 1  # 1 hour lockout

# ============================================================================
# RATE LIMITING & THROTTLING
# ============================================================================

# Django REST Framework throttling (if using DRF)
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # 100 requests per hour for anonymous users
        'user': '1000/hour',  # 1000 requests per hour for authenticated users
    }
}

# ============================================================================
# ADMIN SECURITY
# ============================================================================

# Change default admin URL (add to urls.py instead)
# path('secure-admin-panel-xyz/', admin.site.urls),  # Instead of 'admin/'

# Admin site branding
ADMIN_SITE_HEADER = "CoachJV Secure Admin"
ADMIN_SITE_TITLE = "CoachJV Admin Portal"

# ============================================================================
# DATA PROTECTION & PRIVACY
# ============================================================================

# Sensitive data fields (mark as read-only in admin)
SENSITIVE_FIELDS = [
    'password', 'api_key', 'secret_key', 'private_key',
    'wallet_private_key', 'bank_account', 'ssn'
]

# Data retention policies
USER_DATA_RETENTION_DAYS = 730  # Keep user data for 2 years
LOG_RETENTION_DAYS = 90  # Keep logs for 90 days

# ============================================================================
# FILE UPLOAD SECURITY
# ============================================================================

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']

# ============================================================================
# DATABASE SECURITY
# ============================================================================

# Database connection pooling (if using PostgreSQL)
DATABASES = {
    'default': {
        # ... your existing database config
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'sslmode': 'require',  # Require SSL for database connections
        }
    }
}

# ============================================================================
# LOGGING & MONITORING
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.security': {
            'handlers': ['console', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ============================================================================
# IP WHITELIST / BLACKLIST (Optional)
# ============================================================================

# Whitelist specific IPs for admin access (optional)
# ALLOWED_ADMIN_IPS = ['your.ip.address.here']

# Blacklisted IPs (handled by Cloudflare, but can add here too)
# BLOCKED_IPS = []

# ============================================================================
# ADDITIONAL SECURITY MEASURES
# ============================================================================

# Disable debug mode in production (CRITICAL!)
DEBUG = False

# Only allow specific hosts
ALLOWED_HOSTS = [
    'coachjvtech.us',
    'www.coachjvtech.us',
    'coachjv-crypto.onrender.com',
    '.onrender.com',
]

# Secret key should be in environment variable (already done in render.yaml)
# SECRET_KEY = os.environ.get('SECRET_KEY')

# Disable browsable API in production (if using Django REST Framework)
# REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
#     'rest_framework.renderers.JSONRenderer',
# ]

# ============================================================================
# CLOUDFLARE INTEGRATION
# ============================================================================

# Trust Cloudflare proxy headers
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Get real IP from Cloudflare
# Add to middleware: 'core.middleware.CloudflareMiddleware'

# ============================================================================
# ANTI-BOT MEASURES
# ============================================================================

# Add django-ratelimit or django-defender for additional protection
# pip install django-ratelimit django-defender

# DEFENDER_LOGIN_FAILURE_LIMIT = 5
# DEFENDER_COOLOFF_TIME = 300  # 5 minutes
# DEFENDER_LOCKOUT_TEMPLATE = 'defender/lockout.html'

# ============================================================================
# CORS (if needed for API)
# ============================================================================

# CORS_ALLOWED_ORIGINS = [
#     "https://coachjvtech.us",
#     "https://www.coachjvtech.us",
# ]
# CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# NOTES:
# ============================================================================
# 1. Install required packages:
#    pip install django-csp django-ratelimit django-defender django-axes
#
# 2. Update requirements.txt with security packages
#
# 3. Create Cloudflare middleware to get real IP addresses
#
# 4. Regularly update Django and all dependencies
#
# 5. Enable 2FA for admin users
#
# 6. Regular security audits and penetration testing
#
# 7. Monitor logs for suspicious activity
#
# 8. Keep SECRET_KEY and API keys in environment variables only
#
# 9. Regular database backups
#
# 10. Implement proper error handling (don't expose stack traces)
# ============================================================================
