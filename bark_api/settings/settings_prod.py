from .settings_common import *
import dj_database_url
import os

DEBUG = False

ALLOWED_HOSTS = ['bark.com', 'barkbankapi-e88bfd94ccc1.herokuapp.com']

# Security settings for production
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Ensure Django knows it's behind a proxy and should trust the 'X-Forwarded-Proto' header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files settings (ensure Whitenoise is used for serving static files)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Production database setup - Use DATABASE_URL from Heroku
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# Additional settings for REST Framework, CORS, etc., inherit from settings_common