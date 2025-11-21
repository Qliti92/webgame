"""
Django settings for game topup project.
"""
import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,64.176.85.8').split(',')

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Must be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',  # API documentation
    'django_celery_beat',  # Celery beat for periodic tasks
    'django_celery_results',  # Store celery task results
    'captcha',  # django-simple-captcha

    # Local apps
    'apps.core',
    'apps.users',
    'apps.games',
    'apps.orders',
    'apps.wallets',
    'apps.notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # LocaleMiddleware removed - English only for frontend, Vietnamese for admin
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'frontend' / 'templates',
            BASE_DIR / 'templates',  # For admin templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_appearance',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Using PostgreSQL for production (Docker) and SQLite for local development
import dj_database_url

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL and DATABASE_URL.strip():
    # Production: Use PostgreSQL from DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Authentication Backends - Allow login with email or username
AUTHENTICATION_BACKENDS = [
    'apps.users.backends.EmailOrUsernameBackend',  # Custom backend for email/username login
    'django.contrib.auth.backends.ModelBackend',   # Default backend (fallback)
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password Hashing with Argon2
# Temporarily disabled for quick start - using default PBKDF2
# PASSWORD_HASHERS = [
#     'django.contrib.auth.hashers.Argon2PasswordHasher',
#     'django.contrib.auth.hashers.PBKDF2PasswordHasher',
#     'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
#     'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
# ]

# Internationalization
# Frontend: English only
# Django Admin: Vietnamese (via Django's built-in translations)
LANGUAGE_CODE = 'vi'  # Vietnamese for Django Admin
TIME_ZONE = 'UTC'
USE_I18N = True  # Keep enabled for Django's internal translations
USE_L10N = True
USE_TZ = True

# Multi-language support removed - English only for user-facing pages
# Admin will use Vietnamese through Django's built-in translations

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Frontend static files path
# In Docker: BASE_DIR is /app, frontend is at /app/frontend
# In local dev: BASE_DIR is backend/, frontend is at ../frontend
if Path('/app/frontend/static').exists():
    # Docker environment
    STATICFILES_DIRS = [Path('/app/frontend/static')]
else:
    # Local development
    STATICFILES_DIRS = [BASE_DIR.parent / 'frontend' / 'static']

# Use Whitenoise for serving static files in production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Redis
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Payment Settings
ADMIN_PAYMENT_ADDRESS = config('ADMIN_PAYMENT_ADDRESS', default='')
# Legacy support for old environment variable name
ADMIN_USDT_TRC20_ADDRESS = config('ADMIN_USDT_TRC20_ADDRESS', default=ADMIN_PAYMENT_ADDRESS)
TRON_API_KEY = config('TRON_API_KEY', default='')

# Email Settings
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Rate Limiting
RATELIMIT_ENABLE = config('RATELIMIT_ENABLE', default=True, cast=bool)

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Game TopUp API',
    'DESCRIPTION': 'API for game topup system with crypto payment',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Security Settings for Production
# Only enable SSL redirect if explicitly set (for servers with SSL certificates)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)

if not DEBUG:
    SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT  # Only secure cookies if using SSL
    CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT  # Only secure CSRF if using SSL
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

    # Only enable HSTS if SSL is enabled
    if SECURE_SSL_REDIRECT:
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

# ============================================
# JAZZMIN SETTINGS - Custom Admin UI
# ============================================
JAZZMIN_SETTINGS = {
    # Title on the login screen and admin site
    "site_title": "Game TopUp Admin",
    "site_header": "Game TopUp",
    "site_brand": "Game TopUp Admin",

    # Logo to use for your site (must be present in static files)
    "site_logo": None,  # You can add logo path later: "images/logo.png"
    "login_logo": None,

    # Logo to use for login form in dark mode
    "login_logo_dark": None,

    # CSS classes to add to logo
    "site_logo_classes": "img-circle",

    # Icon to use for site in top navbar (Font Awesome)
    "site_icon": "fas fa-gamepad",

    # Welcome text on the login screen
    "welcome_sign": "Welcome to Game TopUp Admin",

    # Copyright on the footer
    "copyright": "Game TopUp - 2024",

    # Search bar functionality
    "search_model": ["users.User", "games.Game", "orders.Order"],

    # User avatar field
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "users.User"},
        {"app": "games"},
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu
    "hide_apps": [],

    # Hide these models when generating side menu
    "hide_models": [],

    # Order of apps/models in side menu
    "order_with_respect_to": ["users", "games", "orders", "wallets", "notifications"],

    # Custom icons for apps/models (Font Awesome)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.User": "fas fa-user-circle",
        "games.Game": "fas fa-gamepad",
        "games.GamePackage": "fas fa-box",
        "orders.Order": "fas fa-shopping-cart",
        "wallets.UserWallet": "fas fa-wallet",
        "wallets.Deposit": "fas fa-coins",
        "wallets.Withdrawal": "fas fa-money-bill-wave",
        "notifications.Notification": "fas fa-bell",
        "notifications.NotificationPreference": "fas fa-cog",
    },

    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #############
    # UI Tweaks #
    #############

    # Use modals instead of popups for related models
    "related_modal_active": False,

    # Custom CSS/JS
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": None,

    # Use modals for add/change forms
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############

    # Render out the change view as a single form, or in tabs
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "users.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
}

# Jazzmin UI Tweaks
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,  # We'll use custom CSS
    "accent": "accent-primary",
    "navbar": "navbar-dark navbar-primary",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'  # For development, prints to console
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@gametopup.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ==============================================================================
# CAPTCHA CONFIGURATION
# ==============================================================================

# django-simple-captcha settings
CAPTCHA_IMAGE_SIZE = (120, 50)
CAPTCHA_FONT_SIZE = 30
CAPTCHA_BACKGROUND_COLOR = '#f8f9fa'
CAPTCHA_FOREGROUND_COLOR = '#1f2937'
CAPTCHA_LENGTH = 4  # Number of characters
CAPTCHA_TIMEOUT = 5  # Minutes until CAPTCHA expires
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)

# ==============================================================================
# PASSWORD RESET CONFIGURATION
# ==============================================================================

# Password reset token expires in 1 hour
PASSWORD_RESET_TIMEOUT = 3600  # seconds

# ==============================================================================
# RATE LIMITING CONFIGURATION
# ==============================================================================

# Rate limit settings for authentication endpoints
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Max login attempts
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_TIMEOUT = 900  # 15 minutes in seconds

# Max password reset requests
MAX_PASSWORD_RESET_ATTEMPTS = 3
PASSWORD_RESET_ATTEMPT_TIMEOUT = 3600  # 1 hour in seconds

# ==============================================================================
# FRONTEND CONFIGURATION
# ==============================================================================

# Frontend URL for email links
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost')
