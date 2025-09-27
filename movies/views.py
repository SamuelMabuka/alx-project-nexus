from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Avg
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.openapi import OpenApiTypes
from .models import Genre, Movie, Favorite, Rating, Watchlist, UserPreference
from .serializers import (
    GenreSerializer, MovieListSerializer, MovieDetailSerializer,
    FavoriteSerializer, RatingSerializer, RatingCreateUpdateSerializer,
    WatchlistSerializer, WatchlistCreateUpdateSerializer,
    UserPreferenceSerializer, UserPreferenceUpdateSerializer,
    MovieSearchResponseSerializer, ErrorResponseSerializer, SuccessResponseSerializer
)
from .services import tmdb_service
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class GenreListView(generics.ListAPIView):
    """
    API endpoint to list all movie genres.
    
    Fetches genres from TMDb API and caches them locally.
    Available to all users (no authentication required).
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="List Movie Genres",
        description="Get all available movie genres from TMDb",
        responses={
            200: GenreSerializer(many=True),
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all genres with fresh TMDb data."""
        try:
            # Fetch/update genres from TMDb API
            tmdb_genres = tmdb_service.get_genres()
            
            # Return local database genres (updated by service)
            return super().get(request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error fetching genres: {str(e)}")
            return Response(
                {'error': 'Failed to fetch genres', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PopularMoviesView(APIView):
    """
    API endpoint for popular movies from TMDb.
    
    Fetches popular movies with pagination and caches results.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Get Popular Movies",
        description="Fetch popular movies from TMDb API with pagination",
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number (default: 1)',
                default=1
            ),
            OpenApiParameter(
                name='refresh',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Force refresh from TMDb API',
                default=False
            )
        ],
        responses={
            200: MovieSearchResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request):
        """Get popular movies from TMDb API."""
        try:
            page = int(request.query_params.get('page', 1))
            force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'
            
            # Fetch from TMDb API
            tmdb_data = tmdb_service.get_popular_movies(page=page, force_refresh=force_refresh)
            
            if not tmdb_data.get('results'):
                return Response(
                    {'error': 'No popular movies found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get movie IDs and fetch from local database
            movie_ids = [movie['id'] for movie in tmdb_data['results']]
            movies = Movie.objects.filter(tmdb_id__in=movie_ids).prefetch_related('genres')
            
            # Serialize with user context
            serializer = MovieListSerializer(movies, many=True, context={'request': request})
            
            response_data = {
                'results': serializer.data,
                'total_results': tmdb_data.get('total_results', 0),
                'total_pages': tmdb_data.get('total_pages', 0),
                'page': page
            }
            
            logger.info(f"Returned {len(movies)} popular movies for page {page}")
            return Response(response_data)
            
        except ValueError:
            return Response(
                {'error': 'Invalid page number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error fetching popular movies: {str(e)}")
            return Response(
                {'error': 'Failed to fetch popular movies', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TrendingMoviesView(APIView):
    """
    API endpoint for trending movies from TMDb.
    
    Fetches trending movies for day or week periods.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Get Trending Movies",
        description="Fetch trending movies from TMDb API",
        parameters=[
            OpenApiParameter(
                name='time_window',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Time window: "day" or "week"',
                default='day',
                enum=['day', 'week']
            ),
            OpenApiParameter(
                name='refresh',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Force refresh from TMDb API',
                default=False
            )
        ],
        responses={
            200: MovieListSerializer(many=True),
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request):
        """Get trending movies from TMDb API."""
        try:
            time_window = request.query_params.get('time_window', 'day')
            force_refresh = request.query_params.get('refresh', 'false').lower() == 'true'
            
            if time_window not in ['day', 'week']:
                return Response(
                    {'error': 'time_window must be "day" or "week"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Fetch from TMDb API
            tmdb_movies = tmdb_service.get_trending_movies(time_window=time_window, force_refresh=force_refresh)
            
            if not tmdb_movies:
                return Response(
                    {'error': 'No trending movies found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get movie IDs and fetch from local database
            movie_ids = [movie['id'] for movie in tmdb_movies]
            movies = Movie.objects.filter(tmdb_id__in=movie_ids).prefetch_related('genres')
            
            # Serialize with user context
            serializer = MovieListSerializer(movies, many=True, context={'request': request})
            
            logger.info(f"Returned {len(movies)} trending movies ({time_window})")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching trending movies: {str(e)}")
            return Response(
                {'error': 'Failed to fetch trending movies', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MovieDetailView(APIView):
    """
    API endpoint for detailed movie information.
    
    Fetches comprehensive movie data from TMDb and local database.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Get Movie Details",
        description="Get comprehensive movie information",
        responses={
            200: MovieDetailSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request, movie_id):
        """Get detailed movie information."""
        try:
            # Try to get movie from local database first
            try:
                movie = Movie.objects.prefetch_related('genres').get(tmdb_id=movie_id)
                
                # Check if cache is expired and refresh if needed
                if movie.is_cache_expired():
                    logger.info(f"Movie cache expired for ID {movie_id}, refreshing...")
                    tmdb_service.get_movie_details(movie_id, force_refresh=True)
                    movie.refresh_from_db()
                    
            except Movie.DoesNotExist:
                # Movie not in local database, fetch from TMDb
                logger.info(f"Movie {movie_id} not in local database, fetching from TMDb...")
                tmdb_data = tmdb_service.get_movie_details(movie_id)
                
                if not tmdb_data:
                    return Response(
                        {'error': 'Movie not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Get the movie from database (should be created by service)
                movie = Movie.objects.prefetch_related('genres').get(tmdb_id=movie_id)
            
            # Serialize with user context
            serializer = MovieDetailSerializer(movie, context={'request': request})
            
            logger.info(f"Returned movie details for '{movie.title}' (ID: {movie_id})")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching movie details for ID {movie_id}: {str(e)}")
            return Response(
                {'error': 'Failed to fetch movie details', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MovieSearchView(APIView):
    """
    API endpoint for searching movies.
    
    Searches movies on TMDb API with pagination.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Search Movies",
        description="Search movies by title",
        parameters=[
            OpenApiParameter(
                name='query',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query',
                required=True
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number (default: 1)',
                default=1
            )
        ],
        responses={
            200: MovieSearchResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request):
        """Search movies by title."""
        try:
            query = request.query_params.get('query', '').strip()
            page = int(request.query_params.get('page', 1))
            
            if not query:
                return Response(
                    {'error': 'Search query is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(query) < 2:
                return Response(
                    {'error': 'Search query must be at least 2 characters long'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Search on TMDb API
            tmdb_data = tmdb_service.search_movies(query=query, page=page)
            
            if not tmdb_data.get('results'):
                return Response({
                    'results': [],
                    'total_results': 0,
                    'total_pages': 0,
                    'page': page
                })
            
            # Get movie IDs and fetch from local database
            movie_ids = [movie['id'] for movie in tmdb_data['results']]
            movies = Movie.objects.filter(tmdb_id__in=movie_ids).prefetch_related('genres')
            
            # Serialize with user context
            serializer = MovieListSerializer(movies, many=True, context={'request': request})
            
            response_data = {
                'results': serializer.data,
                'total_results': tmdb_data.get('total_results', 0),
                'total_pages': tmdb_data.get('total_pages', 0),
                'page': page
            }
            
            logger.info(f"Search '{query}' returned {len(movies)} movies on page {page}")
            return Response(response_data)
            
        except ValueError:
            return Response(
                {'error': 'Invalid page number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error searching movies with query '{query}': {str(e)}")
            return Response(
                {'error': 'Search failed', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SimilarMoviesView(APIView):
    """
    API endpoint for similar movies.
    
    Gets movies similar to a specific movie from TMDb API.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Get Similar Movies",
        description="Get movies similar to a specific movie",
        responses={
            200: MovieListSerializer(many=True),
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request, movie_id):
        """Get movies similar to the specified movie."""
        try:
            # Fetch similar movies from TMDb API
            similar_movies = tmdb_service.get_similar_movies(movie_id)
            
            if not similar_movies:
                return Response([])  # Return empty list if no similar movies
            
            # Get movie IDs and fetch from local database
            movie_ids = [movie['id'] for movie in similar_movies]
            movies = Movie.objects.filter(tmdb_id__in=movie_ids).prefetch_related('genres')
            
            # Serialize with user context
            serializer = MovieListSerializer(movies, many=True, context={'request': request})
            
            logger.info(f"Returned {len(movies)} similar movies for movie ID {movie_id}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching similar movies for ID {movie_id}: {str(e)}")
            return Response(
                {'error': 'Failed to fetch similar movies', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# User-specific movie interaction views (require authentication)

class FavoriteMoviesView(generics.ListAPIView):
    """
    API endpoint for user's favorite movies.
    
    Lists all movies the authenticated user has marked as favorites.
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return current user's favorites."""
        return Favorite.objects.filter(user=self.request.user).select_related('movie').prefetch_related('movie__genres')
    
    @extend_schema(
        summary="Get User's Favorite Movies",
        description="List all movies the current user has favorited",
        responses={
            200: FavoriteSerializer(many=True),
            401: ErrorResponseSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ToggleFavoriteView(APIView):
    """
    API endpoint to toggle movie favorite status.
    
    Add or remove a movie from user's favorites.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Toggle Movie Favorite",
        description="Add or remove a movie from favorites",
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def post(self, request, movie_id):
        """Toggle favorite status for a movie."""
        try:
            # Get or fetch the movie
            try:
                movie = Movie.objects.get(tmdb_id=movie_id)
            except Movie.DoesNotExist:
                # Try to fetch from TMDb API
                tmdb_data = tmdb_service.get_movie_details(movie_id)
                if not tmdb_data:
                    return Response(
                        {'error': 'Movie not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                movie = Movie.objects.get(tmdb_id=movie_id)
            
            # Toggle favorite status
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                movie=movie
            )
            
            if not created:
                # Already favorited, remove it
                favorite.delete()
                message = f"Removed '{movie.title}' from favorites"
                is_favorited = False
            else:
                # Newly favorited
                message = f"Added '{movie.title}' to favorites"
                is_favorited = True
            
            logger.info(f"User {request.user.email} {'favorited' if is_favorited else 'unfavorited'} movie '{movie.title}'")
            
            return Response({
                'message': message,
                'is_favorited': is_favorited,
                'movie_title': movie.title
            })
            
        except Exception as e:
            logger.error(f"Error toggling favorite for movie ID {movie_id}: {str(e)}")
            return Response(
                {'error': 'Failed to toggle favorite', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserRatingsView(generics.ListAPIView):
    """
    API endpoint for user's movie ratings.
    
    Lists all movies the authenticated user has rated.
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return current user's ratings."""
        return Rating.objects.filter(user=self.request.user).select_related('movie').prefetch_related('movie__genres').order_by('-updated_at')
    
    @extend_schema(
        summary="Get User's Movie Ratings",
        description="List all movies the current user has rated",
        responses={
            200: RatingSerializer(many=True),
            401: ErrorResponseSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class RateMovieView(APIView):
    """
    API endpoint to rate a movie.
    
    Create or update a rating for a specific movie.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Rate Movie",
        description="Rate a movie from 1-5 stars with optional review",
        request=RatingCreateUpdateSerializer,
        responses={
            200: RatingSerializer,
            201: RatingSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def post(self, request, movie_id):
        """Rate a movie."""
        try:
            # Get or fetch the movie
            try:
                movie = Movie.objects.get(tmdb_id=movie_id)
            except Movie.DoesNotExist:
                # Try to fetch from TMDb API
                tmdb_data = tmdb_service.get_movie_details(movie_id)
                if not tmdb_data:
                    return Response(
                        {'error': 'Movie not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                movie = Movie.objects.get(tmdb_id=movie_id)
            
            # Create or update rating
            rating, created = Rating.objects.get_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': 0}  # Temporary default
            )
            
            # Serialize and validate the data
            serializer = RatingCreateUpdateSerializer(rating, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                # Return full rating data
                response_serializer = RatingSerializer(rating, context={'request': request})
                
                action = "Created" if created else "Updated"
                logger.info(f"User {request.user.email} {action.lower()} rating for '{movie.title}': {rating.rating} stars")
                
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error rating movie ID {movie_id}: {str(e)}")
            return Response(
                {'error': 'Failed to rate movie', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Delete Movie Rating",
        description="Remove rating for a movie",
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def delete(self, request, movie_id):
        """Delete a movie rating."""
        try:
            movie = get_object_or_404(Movie, tmdb_id=movie_id)
            rating = get_object_or_404(Rating, user=request.user, movie=movie)
            
            movie_title = movie.title
            rating.delete()
            
            logger.info(f"User {request.user.email} removed rating for '{movie_title}'")
            
            return Response({
                'message': f"Removed rating for '{movie_title}'"
            })
            
        except Exception as e:
            logger.error(f"Error deleting rating for movie ID {movie_id}: {str(e)}")
            return Response(
                {'error': 'Failed to delete rating', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserWatchlistView(generics.ListAPIView):
    """
    API endpoint for user's watchlist.
    
    Lists all movies in the authenticated user's watchlist.
    """
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return current user's watchlist."""
        return Watchlist.objects.filter(user=self.request.user).select_related('movie').prefetch_related('movie__genres').order_by('-created_at')
    
    @extend_schema(
        summary="Get User's Watchlist",
        description="List all movies in the current user's watchlist",
        responses={
            200: WatchlistSerializer(many=True),
            401: ErrorResponseSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ToggleWatchlistView(APIView):
    """
    API endpoint to toggle movie watchlist status.
    
    Add or remove a movie from user's watchlist.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Toggle Movie Watchlist",
        description="Add or remove a movie from watchlist",
        request=WatchlistCreateUpdateSerializer,
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def post(self, request, movie_id):
        """Toggle watchlist status for a movie."""
        try:
            # Get or fetch the movie
            try:
                movie = Movie.objects.get(tmdb_id=movie_id)
            except Movie.DoesNotExist:
                # Try to fetch from TMDb API
                tmdb_data = tmdb_service.get_movie_details(movie_id)
                if not tmdb_data:
                    return Response(
                        {'error': 'Movie not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                movie = Movie.objects.get(tmdb_id=movie_id)
            
            # Check if already in watchlist
            watchlist_item = Watchlist.objects.filter(user=request.user, movie=movie).first()
            
            if watchlist_item:
                # Already in watchlist, remove it
                watchlist_item.delete()
                message = f"Removed '{movie.title}' from watchlist"
                is_in_watchlist = False
            else:
                # Add to watchlist
                serializer = WatchlistCreateUpdateSerializer(data=request.data)
                if serializer.is_valid():
                    Watchlist.objects.create(
                        user=request.user,
                        movie=movie,
                        **serializer.validated_data
                    )
                else:
                    # Use default values if no data provided
                    Watchlist.objects.create(user=request.user, movie=movie)
                
                message = f"Added '{movie.title}' to watchlist"
                is_in_watchlist = True
            
            logger.info(f"User {request.user.email} {'added to' if is_in_watchlist else 'removed from'} watchlist: '{movie.title}'")
            
            return Response({
                'message': message,
                'is_in_watchlist': is_in_watchlist,
                'movie_title': movie.title
            })
            
        except Exception as e:
            logger.error(f"Error toggling watchlist for movie ID {movie_id}: {str(e)}")
            return Response(
                {'error': 'Failed to toggle watchlist', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserPreferencesView(APIView):
    """
    API endpoint for user movie preferences.
    
    Get and update user's movie preferences for recommendations.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get User Movie Preferences",
        description="Get current user's movie preferences",
        responses={
            200: UserPreferenceSerializer,
            401: ErrorResponseSerializer,
        }
    )
    def get(self, request):
        """Get user's movie preferences."""
        try:
            preferences, created = UserPreference.objects.get_or_create(user=request.user)
            serializer = UserPreferenceSerializer(preferences, context={'request': request})
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error fetching user preferences: {str(e)}")
            return Response(
                {'error': 'Failed to fetch preferences', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Update User Movie Preferences",
        description="Update current user's movie preferences",
        request=UserPreferenceUpdateSerializer,
        responses={
            200: UserPreferenceSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        }
    )
    def put(self, request):
        """Update user's movie preferences."""
        try:
            preferences, created = UserPreference.objects.get_or_create(user=request.user)
            
            serializer = UserPreferenceUpdateSerializer(preferences, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                
                # Return updated preferences
                response_serializer = UserPreferenceSerializer(preferences, context={'request': request})
                
                logger.info(f"Updated movie preferences for user {request.user.email}")
                
                return Response(response_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            return Response(
                {'error': 'Failed to update preferences', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RecommendationsView(APIView):
    """
    API endpoint for personalized movie recommendations.
    
    Generate movie recommendations based on user's preferences,
    favorites, ratings, and viewing history.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get Personalized Movie Recommendations",
        description="Get movie recommendations based on user preferences and history",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of recommendations (default: 20, max: 50)',
                default=20
            )
        ],
        responses={
            200: MovieListSerializer(many=True),
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        }
    )
    def get(self, request):
        """Get personalized movie recommendations."""
        try:
            limit = min(int(request.query_params.get('limit', 20)), 50)
            user = request.user
            
            # Get user preferences
            try:
                preferences = UserPreference.objects.get(user=user)
                favorite_genre_ids = list(preferences.favorite_genres.values_list('tmdb_id', flat=True))
                min_rating = preferences.min_rating
                include_adult = preferences.include_adult
            except UserPreference.DoesNotExist:
                favorite_genre_ids = []
                min_rating = 6.0
                include_adult = False
            
            # Get user's favorite and rated movies to avoid recommending them again
            user_movie_ids = set()
            user_movie_ids.update(user.favorites.values_list('movie__tmdb_id', flat=True))
            user_movie_ids.update(user.ratings.values_list('movie__tmdb_id', flat=True))
            
            # Build recommendation query
            recommendations_query = Movie.objects.filter(
                vote_average__gte=min_rating,
                is_active=True
            ).exclude(tmdb_id__in=user_movie_ids).prefetch_related('genres')
            
            # Filter by adult content preference
            if not include_adult:
                recommendations_query = recommendations_query.filter(adult=False)
            
            # Prioritize movies with user's favorite genres
            if favorite_genre_ids:
                genre_movies = recommendations_query.filter(
                    genres__tmdb_id__in=favorite_genre_ids
                ).distinct().order_by('-vote_average', '-popularity')[:limit//2]
                
                # Add general popular movies to fill the rest
                other_movies = recommendations_query.exclude(
                    id__in=[movie.id for movie in genre_movies]
                ).order_by('-popularity', '-vote_average')[:limit - len(genre_movies)]
                
                # Combine recommendations
                recommendations = list(genre_movies) + list(other_movies)
            else:
                # No genre preferences, use popular movies
                recommendations = recommendations_query.order_by('-popularity', '-vote_average')[:limit]
            
            # If we still need more recommendations, get similar movies to user's favorites
            if len(recommendations) < limit and user_movie_ids:
                favorite_movies = user.favorites.select_related('movie')[:3]  # Top 3 favorites
                similar_movie_ids = set()
                
                for favorite in favorite_movies:
                    try:
                        similar_movies = tmdb_service.get_similar_movies(favorite.movie.tmdb_id)
                        similar_movie_ids.update([movie['id'] for movie in similar_movies[:5]])
                    except:
                        continue
                
                # Remove already included movies
                similar_movie_ids -= user_movie_ids
                similar_movie_ids -= set(rec.tmdb_id for rec in recommendations)
                
                if similar_movie_ids:
                    additional_movies = Movie.objects.filter(
                        tmdb_id__in=similar_movie_ids,
                        vote_average__gte=min_rating,
                        is_active=True
                    )
                    
                    if not include_adult:
                        additional_movies = additional_movies.filter(adult=False)
                    
                    additional_movies = additional_movies.order_by('-vote_average')[:limit - len(recommendations)]
                    recommendations.extend(additional_movies)
            
            # Serialize recommendations
            serializer = MovieListSerializer(recommendations, many=True, context={'request': request})
            
            logger.info(f"Generated {len(recommendations)} recommendations for user {user.email}")
            
            return Response(serializer.data)
            
        except ValueError:
            return Response(
                {'error': 'Invalid limit parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error generating recommendations for user {request.user.email}: {str(e)}")
            return Response(
                {'error': 'Failed to generate recommendations', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Statistics and utility views

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_movie_stats(request):
    """
    Get user's movie statistics.
    
    Returns stats like total favorites, ratings, watchlist count, etc.
    """
    try:
        user = request.user
        
        # Calculate statistics
        stats = {
            'total_favorites': user.favorites.count(),
            'total_ratings': user.ratings.count(),
            'watchlist_count': user.watchlist.count(),
            'average_rating_given': user.ratings.aggregate(avg=Avg('rating'))['avg'],
            'favorite_genres': [],
        }
        
        # Round average rating
        if stats['average_rating_given']:
            stats['average_rating_given'] = round(stats['average_rating_given'], 1)
        
        # Get favorite genres from preferences
        try:
            preferences = UserPreference.objects.get(user=user)
            stats['favorite_genres'] = [
                {'id': genre.id, 'name': genre.name} 
                for genre in preferences.favorite_genres.all()[:5]
            ]
        except UserPreference.DoesNotExist:
            pass
        
        # Get most rated genre
        if user.ratings.exists():
            from django.db.models import Count
            most_rated_genre = user.ratings.values(
                'movie__genres__name'
            ).annotate(
                count=Count('movie__genres__name')
            ).order_by('-count').first()
            
            if most_rated_genre and most_rated_genre['movie__genres__name']:
                stats['most_rated_genre'] = {
                    'name': most_rated_genre['movie__genres__name'],
                    'count': most_rated_genre['count']
                }
        
        logger.info(f"Generated movie statistics for user {user.email}")
        
        return Response({
            'message': 'User movie statistics retrieved',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error generating user movie stats: {str(e)}")
        return Response(
            {'error': 'Failed to generate statistics', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
