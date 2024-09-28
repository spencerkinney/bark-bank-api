from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
import os

is_production = os.getenv('DJANGO_PRODUCTION') == 'True'

schema_view = get_schema_view(
   openapi.Info(
      title="Bark Banking API",
      default_version='v1',
      description="API for Bark banking operations.\nBark Technologies is a financial technology company, not a bank.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@barkbank.local"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   schemes=['https'] if is_production else ['http'],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('bark_core.urls')),
    path('token/', obtain_auth_token, name='api_token_auth'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]