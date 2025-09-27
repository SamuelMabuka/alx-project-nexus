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

def api_root(request):
    """Main API entry point with navigation."""
    base_url = request.build_absolute_uri('/')
    
    return JsonResponse({
        'welcome': 'Nexus Movie Recommendation API',
        'version': '1.0.0',
        'status': 'live',
        'base_url': base_url,
        
        # Quick Actions - Direct links users can click
        'quick_actions': {
            'browse_api_docs': f'{base_url}api/docs/',
            'test_search': f'{base_url}api/movies/search/?query=avengers',
            'view_popular_movies': f'{base_url}api/movies/popular/',
            'view_trending': f'{base_url}api/movies/trending/',
            'health_check': f'{base_url}health/',
        },
        
        # Main API Sections
        'api_sections': {
            'authentication': {
                'base': f'{base_url}api/auth/',
                'description': 'User registration, login, and profile management',
                'endpoints': {
                    'register': f'{base_url}api/auth/register/',
                    'login': f'{base_url}api/auth/login/',
                    'profile': f'{base_url}api/auth/profile/',
                    'change_password': f'{base_url}api/auth/change-password/',
                    'logout': f'{base_url}api/auth/logout/'
                }
            },
            'movies': {
                'base': f'{base_url}api/movies/',
                'description': 'Movie discovery, search, and user interactions',
                'endpoints': {
                    'search': f'{base_url}api/movies/search/?query=YOUR_SEARCH',
                    'popular': f'{base_url}api/movies/popular/',
                    'trending': f'{base_url}api/movies/trending/',
                    'genres': f'{base_url}api/movies/genres/',
                    'movie_details': f'{base_url}api/movies/550/',
                    'favorites': f'{base_url}api/movies/favorites/',
                    'ratings': f'{base_url}api/movies/ratings/',
                    'watchlist': f'{base_url}api/movies/watchlist/',
                    'recommendations': f'{base_url}api/movies/recommendations/',
                    'user_stats': f'{base_url}api/movies/stats/'
                }
            },
            'admin': {
                'base': f'{base_url}admin/',
                'description': 'Django administration interface',
                'note': 'Requires superuser credentials'
            }
        },
        
        # Documentation & Tools
        'documentation': {
            'interactive_docs': f'{base_url}api/docs/',
            'api_schema': f'{base_url}api/schema/',
            'browsable_api': 'Click any endpoint above to explore interactively'
        },
        
        # Features Summary
        'features': [
            'JWT Authentication System',
            'Movie Search & Discovery',
            'User Ratings & Reviews', 
            'Favorites & Watchlist Management',
            'Personalized Recommendations',
            'User Statistics & Preferences',
            'Interactive API Documentation'
        ],
        
        # Usage Instructions
        'getting_started': {
            '1_explore': 'Visit /api/docs/ for interactive documentation',
            '2_register': 'POST to /api/auth/register/ to create account',
            '3_login': 'POST to /api/auth/login/ to get JWT tokens',
            '4_search': 'GET /api/movies/search/?query=YOUR_SEARCH to find movies',
            '5_interact': 'Use JWT token to rate, favorite, and get recommendations'
        }
    })

urlpatterns = [
    # Root endpoint - ADD THIS
    path('', api_root, name='api-root'),
    
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
