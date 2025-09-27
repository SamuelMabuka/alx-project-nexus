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
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Nexus Movie API',
        'version': '1.0.0',
        'timestamp': '2025-09-27'
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
                <a href="/api/movies/" class="api-link">🎬 Movies API</a>
                <a href="/api/auth/" class="api-link">🔐 Auth API</a>
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
    """Clean API root with basic information."""
    return JsonResponse({
        'message': 'Welcome to Nexus Movie API',
        'version': '1.0.0',
        'status': 'live',
        'endpoints': {
            'health': '/health/',
            'search_interface': '/search/',
            'api_documentation': '/api/docs/',
            'authentication': '/api/auth/',
            'movies': '/api/movies/',
            'admin': '/admin/'
        },
        'documentation': 'Visit /api/docs/ for complete API documentation'
    })

urlpatterns = [
    # Root endpoint - Clean and simple
    path('', api_root, name='api-root'),
    
    # Search interface
    path('search/', search_page, name='search-page'),
    
    # Core endpoints
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Application endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/movies/', include('movies.urls')),
]

# Custom admin configuration
admin.site.site_header = "Nexus Movie Backend Administration"
admin.site.site_title = "Nexus Movie Admin"
admin.site.index_title = "Welcome to Nexus Movie Administration"
