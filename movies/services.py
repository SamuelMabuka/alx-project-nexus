import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.core.cache import cache
from .models import Movie, Genre, MovieGenre


logger = logging.getLogger(__name__)


class TMDbService:
    """Service class for interacting with The Movie Database API"""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key}
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to TMDb API with error handling"""
        if not self.api_key:
            logger.error("TMDb API key not configured")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None
    
    def get_trending_movies(self, time_window: str = 'week', page: int = 1) -> Optional[Dict]:
        """Get trending movies from TMDb"""
        cache_key = f"trending_movies_{time_window}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request(f"trending/movie/{time_window}", {'page': page})
        
        if data:
            cache.set(cache_key, data, timeout=settings.CACHE_TTL)
        
        return data
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """Get popular movies from TMDb"""
        cache_key = f"popular_movies_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request("movie/popular", {'page': page})
        
        if data:
            cache.set(cache_key, data, timeout=settings.CACHE_TTL)
        
        return data
    
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """Get movie recommendations from TMDb"""
        cache_key = f"movie_recommendations_{movie_id}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request(f"movie/{movie_id}/recommendations", {'page': page})
        
        if data:
            cache.set(cache_key, data, timeout=settings.CACHE_TTL)
        
        return data
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed movie information from TMDb"""
        cache_key = f"movie_details_{movie_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request(f"movie/{movie_id}")
        
        if data:
            cache.set(cache_key, data, timeout=settings.CACHE_TTL * 2)  # Cache longer for details
        
        return data
    
    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """Search for movies by title"""
        cache_key = f"search_movies_{query}_{page}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request("search/movie", {'query': query, 'page': page})
        
        if data:
            cache.set(cache_key, data, timeout=settings.CACHE_TTL)
        
        return data
    
    def get_genres(self) -> Optional[Dict]:
        """Get list of movie genres from TMDb"""
        cache_key = "movie_genres"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        data = self._make_request("genre/movie/list")
        
        if data:
            cache.set(cache_key, data, timeout=settings.CACHE_TTL * 24)  # Cache for 6 hours
        
        return data
    
    def sync_movie_to_db(self, movie_data: Dict) -> Optional[Movie]:
        """Sync movie data from TMDb to local database"""
        try:
            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_data['id'],
                defaults={
                    'title': movie_data.get('title', ''),
                    'original_title': movie_data.get('original_title', ''),
                    'overview': movie_data.get('overview', ''),
                    'poster_path': movie_data.get('poster_path', ''),
                    'backdrop_path': movie_data.get('backdrop_path', ''),
                    'release_date': movie_data.get('release_date') or None,
                    'adult': movie_data.get('adult', False),
                    'original_language': movie_data.get('original_language', ''),
                    'popularity': movie_data.get('popularity', 0.0),
                    'vote_average': movie_data.get('vote_average', 0.0),
                    'vote_count': movie_data.get('vote_count', 0),
                }
            )
            
            # Sync genres if available
            if 'genre_ids' in movie_data:
                self._sync_movie_genres(movie, movie_data['genre_ids'])
            
            return movie
        except Exception as e:
            logger.error(f"Failed to sync movie to database: {e}")
            return None
    
    def _sync_movie_genres(self, movie: Movie, genre_ids: List[int]):
        """Sync movie genres to database"""
        # Clear existing genre relationships
        MovieGenre.objects.filter(movie=movie).delete()
        
        # Add new genre relationships
        for genre_id in genre_ids:
            try:
                genre = Genre.objects.get(tmdb_id=genre_id)
                MovieGenre.objects.create(movie=movie, genre=genre)
            except Genre.DoesNotExist:
                logger.warning(f"Genre with TMDb ID {genre_id} not found in database")
    
    def sync_genres_to_db(self):
        """Sync genres from TMDb to local database"""
        genres_data = self.get_genres()
        if not genres_data or 'genres' not in genres_data:
            return
        
        for genre_data in genres_data['genres']:
            Genre.objects.update_or_create(
                tmdb_id=genre_data['id'],
                defaults={'name': genre_data['name']}
            )
        
        logger.info(f"Synced {len(genres_data['genres'])} genres to database")


# Global instance
tmdb_service = TMDbService()