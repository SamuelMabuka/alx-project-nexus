"""
URL configuration for movie_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Nexus Movie API',
        'version': '1.0.0'
    })

urlpatterns = [
    # Admin and core endpoints
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Authentication endpoints (keep these - they work)
    path('api/auth/', include('accounts.urls')),
    
    # Movie endpoints - NOW WORKING WITH SIMPLE VIEWS
    path('api/movies/', include('movies.urls')),
]

# Custom admin configuration
admin.site.site_header = "Nexus Movie Backend Administration"
admin.site.site_title = "Nexus Movie Admin"
admin.site.index_title = "Welcome to Nexus Movie Administration"
