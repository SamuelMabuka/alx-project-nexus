# movies/urls.py
from django.urls import path
from django.http import JsonResponse
from . import views

def movies_info(request):
    """Base movies info endpoint."""
    return JsonResponse({
        'message': 'Nexus Movie API - Movies Service',
        'version': '1.0.0',
        'endpoints': {
            'info': '/api/movies/',
            'genres': '/api/movies/genres/',
            'popular': '/api/movies/popular/',
            'trending': '/api/movies/trending/',
            'search': '/api/movies/search/',
            'movie_detail': '/api/movies/<id>/',
        },
        'features': {
            'tmdb_integration': 'The Movie Database API',
            'user_favorites': 'Personal movie collections',
            'ratings': 'User movie ratings',
            'recommendations': 'Personalized suggestions'
        },
        'status': 'available',
        'authentication': {
            'public_endpoints': ['genres', 'popular', 'trending', 'search', 'movie_detail'],
            'auth_required': ['favorites', 'ratings', 'watchlist', 'recommendations']
        }
    })

urlpatterns = [
    # Base movies info endpoint
    path('', movies_info, name='movies-info'),
    
    # Public movie endpoints
    path('genres/', views.genres_list, name='genres-list'),
    path('popular/', views.popular_movies, name='popular-movies'),
    path('trending/', views.trending_movies, name='trending-movies'),
    path('search/', views.search_movies, name='search-movies'),
    path('<int:movie_id>/', views.movie_detail, name='movie-detail'),
]

"""
========================================
COMPLETE API ENDPOINTS REFERENCE
========================================

🎬 MOVIE DATA ENDPOINTS (Public Access):
┌─────────────────────────────────────┬──────────────────────────────────┐
│ GET  /api/movies/genres/            │ Get all movie genres             │
│ GET  /api/movies/popular/           │ Get popular movies (paginated)   │
│ GET  /api/movies/trending/          │ Get trending movies (day/week)   │
│ GET  /api/movies/search/            │ Search movies by title           │
│ GET  /api/movies/<id>/              │ Get movie details                │
│ GET  /api/movies/<id>/similar/      │ Get similar movies               │
└─────────────────────────────────────┴──────────────────────────────────┘

⭐ USER INTERACTION ENDPOINTS (Auth Required):
┌─────────────────────────────────────┬──────────────────────────────────┐
│ GET  /api/movies/favorites/         │ Get user's favorite movies       │
│ POST /api/movies/<id>/favorite/     │ Add/remove movie from favorites  │
│ GET  /api/movies/ratings/           │ Get user's movie ratings         │
│ POST /api/movies/<id>/rate/         │ Rate movie (1-5 stars + review)  │
│ DEL  /api/movies/<id>/rate/         │ Delete movie rating              │
│ GET  /api/movies/watchlist/         │ Get user's watchlist             │
│ POST /api/movies/<id>/watchlist/    │ Add/remove from watchlist        │
└─────────────────────────────────────┴──────────────────────────────────┘

🔧 PERSONALIZATION ENDPOINTS (Auth Required):
┌─────────────────────────────────────┬──────────────────────────────────┐
│ GET  /api/movies/preferences/       │ Get user movie preferences       │
│ PUT  /api/movies/preferences/       │ Update user preferences          │
│ GET  /api/movies/recommendations/   │ Get personalized recommendations │
│ GET  /api/movies/stats/             │ Get user movie statistics        │
└─────────────────────────────────────┴──────────────────────────────────┘

========================================
QUERY PARAMETERS REFERENCE
========================================

Popular Movies:
  ?page=1            - Page number (default: 1)
  ?refresh=true      - Force refresh from TMDb API

Trending Movies:
  ?time_window=day   - 'day' or 'week' (default: day)
  ?refresh=true      - Force refresh from TMDb API

Search Movies:
  ?query=spider      - Search query (required, min 2 chars)
  ?page=1            - Page number (default: 1)

Recommendations:
  ?limit=20          - Number of recommendations (default: 20, max: 50)

========================================
AUTHENTICATION REQUIREMENTS
========================================

✅ Public Endpoints (No Auth Required):
- Movie discovery (popular, trending, search)
- Movie details and similar movies
- Genre listings

🔐 Private Endpoints (JWT Token Required):
- All user interactions (favorites, ratings, watchlist)
- User preferences and recommendations
- User statistics

🔑 Authentication Header Format:
Authorization: Bearer <your_jwt_access_token>

========================================
EXAMPLE API CALLS
========================================

# Get popular movies
GET /api/movies/popular/?page=1

# Search for movies
GET /api/movies/search/?query=avengers&page=1

# Get movie details
GET /api/movies/550/  # Fight Club

# Add to favorites (authenticated)
POST /api/movies/550/favorite/
Headers: Authorization: Bearer <token>

# Rate a movie (authenticated)
POST /api/movies/550/rate/
Headers: Authorization: Bearer <token>
Body: {"rating": 5, "review": "Amazing movie!"}

# Get personalized recommendations (authenticated)
GET /api/movies/recommendations/?limit=10
Headers: Authorization: Bearer <token>
"""