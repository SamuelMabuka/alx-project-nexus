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
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
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

def search_page(request):
    """Simple HTML search interface."""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎬 Nexus Movie Search</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #2c3e50; }
            .search-form { margin-bottom: 20px; }
            .search-input { width: 70%; padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 5px; }
            .search-button { padding: 12px 20px; font-size: 16px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px; }
            .search-button:hover { background: #2980b9; }
            .quick-buttons { margin-bottom: 20px; }
            .quick-btn { padding: 8px 15px; margin: 5px; background: #ecf0f1; border: none; border-radius: 15px; cursor: pointer; }
            .quick-btn:hover { background: #d5dbdb; }
            .results { margin-top: 20px; }
            .movie-result { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
            .api-links { text-align: center; margin-top: 30px; }
            .api-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎬 Nexus Movie Search</h1>
                <p>Search for movies using our API</p>
            </div>
            
            <div class="search-form">
                <input type="text" id="searchInput" class="search-input" placeholder="Enter movie name..." onkeypress="handleKeyPress(event)">
                <button onclick="searchMovies()" class="search-button">🔍 Search</button>
            </div>
            
            <div class="quick-buttons">
                <strong>Quick searches:</strong><br>
                <button class="quick-btn" onclick="quickSearch('avengers')">Avengers</button>
                <button class="quick-btn" onclick="quickSearch('batman')">Batman</button>
                <button class="quick-btn" onclick="quickSearch('spider-man')">Spider-Man</button>
                <button class="quick-btn" onclick="quickSearch('marvel')">Marvel</button>
            </div>
            
            <div id="loading" style="display:none; text-align:center; color:#666;">🎬 Searching movies...</div>
            <div id="results" class="results"></div>
            
            <div class="api-links">
                <a href="/api/docs/" class="api-link">📖 API Docs</a>
                <a href="/api/movies/popular/" class="api-link">🔥 Popular</a>
                <a href="/" class="api-link">🏠 API Home</a>
            </div>
        </div>
        
        <script>
            function handleKeyPress(event) {
                if (event.key === 'Enter') searchMovies();
            }
            
            function quickSearch(query) {
                document.getElementById('searchInput').value = query;
                searchMovies();
            }
            
            function searchMovies() {
                const query = document.getElementById('searchInput').value.trim();
                if (!query) return alert('Please enter a movie name!');
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').innerHTML = '';
                
                fetch(`/api/movies/search/?query=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('results').innerHTML = `
                            <div class="movie-result">
                                <h3>✅ Search Results for: "${query}"</h3>
                                <p><strong>Status:</strong> ${data.status}</p>
                                <p><strong>API Response:</strong></p>
                                <pre style="background:#f1f1f1; padding:10px; overflow:auto;">${JSON.stringify(data, null, 2)}</pre>
                            </div>
                        `;
                    })
                    .catch(error => {
                        document.getElementById('loading').style.display = 'none';
                        document.getElementById('results').innerHTML = `
                            <div class="movie-result" style="border-left-color: #e74c3c;">
                                <h3>❌ Error</h3>
                                <p>Could not search movies. Please try again.</p>
                            </div>
                        `;
                    });
            }
        </script>
    </body>
    </html>
    '''
    return HttpResponse(html)

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
            'search_interface': f'{base_url}search/',  # ADD THIS LINE
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
            'search_interface': f'{base_url}search/',  # ADD THIS LINE
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
            '2_search': 'Visit /search/ for simple search interface',  # ADD THIS LINE
            '3_register': 'POST to /api/auth/register/ to create account',
            '4_login': 'POST to /api/auth/login/ to get JWT tokens',
            '5_interact': 'Use JWT token to rate, favorite, and get recommendations'
        }
    })

urlpatterns = [
    # Root endpoint
    path('', api_root, name='api-root'),
    
    # Simple search interface - ADD THIS LINE
    path('search/', search_page, name='search-page'),
    
    # Admin and core endpoints
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Authentication endpoints
    path('api/auth/', include('accounts.urls')),
    
    # Movie endpoints
    path('api/movies/', include('movies.urls')),
]

# Custom admin configuration
admin.site.site_header = "Nexus Movie Backend Administration"
admin.site.site_title = "Nexus Movie Admin"
admin.site.index_title = "Welcome to Nexus Movie Administration"
