# movies/services.py
import requests
import logging
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .models import Movie, Genre

logger = logging.getLogger(__name__)

class TMDbService:
    """
    Service class for interacting with TMDb (The Movie Database) API.
    
    Handles API requests, caching, error handling, and data transformation.
    Reduces API calls through intelligent caching strategies.
    """
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = settings.TMDB_IMAGE_BASE_URL
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Nexus Movie Backend/1.0',
            'Accept': 'application/json',
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make authenticated request to TMDb API.
        
        Args:
            endpoint: API endpoint (e.g., 'movie/popular')
            params: Additional query parameters
            
        Returns:
            JSON response data or None if error
        """
        if not self.api_key:
            logger.error("TMDb API key not configured")
            return None
        
        # Prepare parameters
        request_params = {'api_key': self.api_key}
        if params:
            request_params.update(params)
        
        # Make request
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=request_params, timeout=10)
            response.raise_for_status()
            
            logger.info(f"TMDb API request successful: {endpoint}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed for {endpoint}: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Invalid JSON response from TMDb API: {str(e)}")
            return None
    
    def get_genres(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get movie genres from TMDb API with caching.
        
        Args:
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            List of genre dictionaries
        """
        cache_key = 'tmdb_genres'
        
        # Try cache first (unless force refresh)
        if not force_refresh:
            cached_genres = cache.get(cache_key)
            if cached_genres:
                logger.info("Returning cached genres")
                return cached_genres
        
        # Fetch from API
        logger.info("Fetching genres from TMDb API")
        data = self._make_request('genre/movie/list')
        
        if data and 'genres' in data:
            genres = data['genres']
            
            # Cache for 1 week (genres don't change often)
            cache.set(cache_key, genres, settings.CACHE_TTL['GENRES'])
            
            # Update local database
            self._sync_genres_to_db(genres)
            
            return genres
        
        logger.error("Failed to fetch genres from TMDb")
        return []
    
    def get_popular_movies(self, page: int = 1, force_refresh: bool = False) -> Dict:
        """
        Get popular movies from TMDb API with caching.
        
        Args:
            page: Page number (1-based)
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            Dictionary with movies and pagination info
        """
        cache_key = f'tmdb_popular_movies_page_{page}'
        
        # Try cache first
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached popular movies page {page}")
                return cached_data
        
        # Fetch from API
        logger.info(f"Fetching popular movies page {page} from TMDb API")
        data = self._make_request('movie/popular', {'page': page})
        
        if data:
            # Cache for 1 hour
            cache.set(cache_key, data, settings.CACHE_TTL['POPULAR_MOVIES'])
            
            # Sync movies to local database
            if 'results' in data:
                self._sync_movies_to_db(data['results'])
            
            return data
        
        logger.error(f"Failed to fetch popular movies page {page}")
        return {'results': [], 'total_pages': 0, 'total_results': 0}
    
    def get_trending_movies(self, time_window: str = 'day', force_refresh: bool = False) -> List[Dict]:
        """
        Get trending movies from TMDb API.
        
        Args:
            time_window: 'day' or 'week'
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            List of trending movie dictionaries
        """
        cache_key = f'tmdb_trending_movies_{time_window}'
        
        # Try cache first
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached trending movies ({time_window})")
                return cached_data
        
        # Fetch from API
        logger.info(f"Fetching trending movies ({time_window}) from TMDb API")
        data = self._make_request(f'trending/movie/{time_window}')
        
        if data and 'results' in data:
            movies = data['results']
            
            # Cache for 30 minutes (trending changes frequently)
            cache.set(cache_key, movies, settings.CACHE_TTL['TRENDING_MOVIES'])
            
            # Sync movies to local database
            self._sync_movies_to_db(movies)
            
            return movies
        
        logger.error(f"Failed to fetch trending movies ({time_window})")
        return []
    
    def get_movie_details(self, movie_id: int, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get detailed movie information from TMDb API.
        
        Args:
            movie_id: TMDb movie ID
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            Movie details dictionary or None
        """
        cache_key = f'tmdb_movie_details_{movie_id}'
        
        # Try cache first
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached movie details for ID {movie_id}")
                return cached_data
        
        # Fetch from API
        logger.info(f"Fetching movie details for ID {movie_id} from TMDb API")
        data = self._make_request(f'movie/{movie_id}')
        
        if data:
            # Cache for 24 hours (movie details don't change often)
            cache.set(cache_key, data, settings.CACHE_TTL['MOVIE_DETAILS'])
            
            # Sync movie to local database
            self._sync_movie_to_db(data)
            
            return data
        
        logger.error(f"Failed to fetch movie details for ID {movie_id}")
        return None
    
    def search_movies(self, query: str, page: int = 1, force_refresh: bool = False) -> Dict:
        """
        Search movies on TMDb API.
        
        Args:
            query: Search query
            page: Page number
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            Search results dictionary
        """
        cache_key = f'tmdb_search_{query.lower().replace(" ", "_")}_page_{page}'
        
        # Try cache first
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached search results for '{query}' page {page}")
                return cached_data
        
        # Fetch from API
        logger.info(f"Searching movies for '{query}' page {page} on TMDb API")
        data = self._make_request('search/movie', {'query': query, 'page': page})
        
        if data:
            # Cache for 15 minutes
            cache.set(cache_key, data, settings.CACHE_TTL['SEARCH_RESULTS'])
            
            # Sync movies to local database
            if 'results' in data:
                self._sync_movies_to_db(data['results'])
            
            return data
        
        logger.error(f"Failed to search movies for '{query}'")
        return {'results': [], 'total_pages': 0, 'total_results': 0}
    
    def get_similar_movies(self, movie_id: int, force_refresh: bool = False) -> List[Dict]:
        """
        Get movies similar to a specific movie.
        
        Args:
            movie_id: TMDb movie ID
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            List of similar movie dictionaries
        """
        cache_key = f'tmdb_similar_movies_{movie_id}'
        
        # Try cache first
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Returning cached similar movies for ID {movie_id}")
                return cached_data
        
        # Fetch from API
        logger.info(f"Fetching similar movies for ID {movie_id} from TMDb API")
        data = self._make_request(f'movie/{movie_id}/similar')
        
        if data and 'results' in data:
            movies = data['results']
            
            # Cache for 1 hour
            cache.set(cache_key, movies, settings.CACHE_TTL['RECOMMENDATIONS'])
            
            # Sync movies to local database
            self._sync_movies_to_db(movies)
            
            return movies
        
        logger.error(f"Failed to fetch similar movies for ID {movie_id}")
        return []
    
    def _sync_genres_to_db(self, genres: List[Dict]) -> None:
        """Sync genre data to local database."""
        for genre_data in genres:
            try:
                Genre.objects.update_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
            except Exception as e:
                logger.error(f"Failed to sync genre {genre_data.get('name', 'Unknown')}: {str(e)}")
        
        logger.info(f"Synced {len(genres)} genres to database")
    
    def _sync_movies_to_db(self, movies: List[Dict]) -> None:
        """Sync movie list to local database (basic info only)."""
        synced_count = 0
        
        for movie_data in movies:
            try:
                if self._sync_movie_to_db(movie_data, basic_only=True):
                    synced_count += 1
            except Exception as e:
                logger.error(f"Failed to sync movie {movie_data.get('title', 'Unknown')}: {str(e)}")
        
        logger.info(f"Synced {synced_count} movies to database")
    
    def _sync_movie_to_db(self, movie_data: Dict, basic_only: bool = False) -> bool:
        """
        Sync individual movie to local database.
        
        Args:
            movie_data: Movie data from TMDb API
            basic_only: Only sync basic fields (for list views)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare movie data
            movie_fields = {
                'title': movie_data.get('title', ''),
                'original_title': movie_data.get('original_title', ''),
                'overview': movie_data.get('overview', ''),
                'vote_average': movie_data.get('vote_average', 0.0),
                'vote_count': movie_data.get('vote_count', 0),
                'popularity': movie_data.get('popularity', 0.0),
                'poster_path': movie_data.get('poster_path', ''),
                'backdrop_path': movie_data.get('backdrop_path', ''),
                'adult': movie_data.get('adult', False),
                'original_language': movie_data.get('original_language', 'en'),
                'last_updated_from_tmdb': timezone.now(),
            }
            
            # Add release date if present
            if movie_data.get('release_date'):
                try:
                    movie_fields['release_date'] = datetime.strptime(
                        movie_data['release_date'], '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass
            
            # Add detailed fields if not basic_only
            if not basic_only:
                movie_fields.update({
                    'tagline': movie_data.get('tagline', ''),
                    'runtime': movie_data.get('runtime'),
                    'budget': movie_data.get('budget'),
                    'revenue': movie_data.get('revenue'),
                    'imdb_id': movie_data.get('imdb_id', ''),
                    'status': movie_data.get('status', 'Released'),
                    'production_countries': movie_data.get('production_countries', []),
                    'spoken_languages': movie_data.get('spoken_languages', []),
                })
            
            # Create or update movie
            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_data['id'],
                defaults=movie_fields
            )
            
            # Sync genres if present
            if 'genres' in movie_data:
                genre_ids = [genre['id'] for genre in movie_data['genres']]
                genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                movie.genres.set(genres)
            elif 'genre_ids' in movie_data:
                genres = Genre.objects.filter(tmdb_id__in=movie_data['genre_ids'])
                movie.genres.set(genres)
            
            action = "Created" if created else "Updated"
            logger.info(f"{action} movie: {movie.title}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync movie data: {str(e)}")
            return False
    
    def get_configuration(self) -> Dict:
        """Get TMDb API configuration (image sizes, etc.)."""
        cache_key = 'tmdb_configuration'
        
        # Try cache first (configuration rarely changes)
        cached_config = cache.get(cache_key)
        if cached_config:
            return cached_config
        
        # Fetch from API
        data = self._make_request('configuration')
        
        if data:
            # Cache for 1 week
            cache.set(cache_key, data, 7 * 24 * 60 * 60)
            return data
        
        # Return default configuration if API fails
        return {
            'images': {
                'base_url': 'https://image.tmdb.org/t/p/',
                'poster_sizes': ['w154', 'w185', 'w342', 'w500', 'w780', 'original'],
                'backdrop_sizes': ['w300', 'w780', 'w1280', 'original']
            }
        }

# Create service instance for easy importing
tmdb_service = TMDbService()