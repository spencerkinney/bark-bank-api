import os

from django.core.wsgi import get_wsgi_application

# Set the default settings module to production
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bark_api.settings.settings_dev")

# Override with development settings if DJANGO_DEVELOPMENT env var is set
if os.environ.get("DJANGO_PRODUCTION") == "true":
    os.environ["DJANGO_SETTINGS_MODULE"] = "bark_api.settings.settings_prod"

application = get_wsgi_application()