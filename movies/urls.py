# movies/urls.py
from django.urls import path
from .views import (
    # Movie data views
    GenreListView,
    PopularMoviesView,
    TrendingMoviesView,
    MovieDetailView,
    MovieSearchView,
    SimilarMoviesView,
    
    # User interaction views
    FavoriteMoviesView,
    ToggleFavoriteView,
    UserRatingsView,
    RateMovieView,
    UserWatchlistView,
    ToggleWatchlistView,
    
    # Preferences and recommendations
    UserPreferencesView,
    RecommendationsView,
    
    # Statistics
    user_movie_stats,
)

# URL patterns for movies app
urlpatterns = [
    # ==========================================
    # MOVIE DATA ENDPOINTS (Public Access)
    # ==========================================
    
    # Genres
    path('genres/', GenreListView.as_view(), name='movie-genres'),
    
    # Movie discovery
    path('popular/', PopularMoviesView.as_view(), name='popular-movies'),
    path('trending/', TrendingMoviesView.as_view(), name='trending-movies'),
    path('search/', MovieSearchView.as_view(), name='search-movies'),
    
    # Individual movies
    path('<int:movie_id>/', MovieDetailView.as_view(), name='movie-detail'),
    path('<int:movie_id>/similar/', SimilarMoviesView.as_view(), name='similar-movies'),
    
    # ==========================================
    # USER INTERACTION ENDPOINTS (Auth Required)
    # ==========================================
    
    # Favorites management
    path('favorites/', FavoriteMoviesView.as_view(), name='user-favorites'),
    path('<int:movie_id>/favorite/', ToggleFavoriteView.as_view(), name='toggle-favorite'),
    
    # Ratings management
    path('ratings/', UserRatingsView.as_view(), name='user-ratings'),
    path('<int:movie_id>/rate/', RateMovieView.as_view(), name='rate-movie'),
    
    # Watchlist management
    path('watchlist/', UserWatchlistView.as_view(), name='user-watchlist'),
    path('<int:movie_id>/watchlist/', ToggleWatchlistView.as_view(), name='toggle-watchlist'),
    
    # ==========================================
    # PERSONALIZATION ENDPOINTS (Auth Required)
    # ==========================================
    
    # User preferences
    path('preferences/', UserPreferencesView.as_view(), name='user-preferences'),
    
    # Recommendations
    path('recommendations/', RecommendationsView.as_view(), name='movie-recommendations'),
    
    # Statistics
    path('stats/', user_movie_stats, name='user-movie-stats'),
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