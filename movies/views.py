from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Movie, UserFavorite
from .serializers import (
    MovieSerializer, 
    UserFavoriteSerializer, 
    TMDbMovieSerializer,
    TrendingMoviesResponseSerializer,
    MovieRecommendationsResponseSerializer
)
from .services import tmdb_service


class TrendingMoviesView(generics.ListAPIView):
    """API endpoint for fetching trending movies from TMDb"""
    permission_classes = [AllowAny]
    serializer_class = TrendingMoviesResponseSerializer
    
    @extend_schema(
        summary="Get trending movies",
        description="Fetch trending movies from TMDb API with caching",
        parameters=[
            OpenApiParameter(
                name='time_window',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Time window for trending movies (day/week)",
                enum=['day', 'week'],
                default='week'
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination",
                default=1
            ),
        ],
        responses={200: TrendingMoviesResponseSerializer}
    )
    def get(self, request, *args, **kwargs):
        time_window = request.query_params.get('time_window', 'week')
        page = int(request.query_params.get('page', 1))
        
        if time_window not in ['day', 'week']:
            return Response(
                {'error': 'time_window must be either "day" or "week"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = tmdb_service.get_trending_movies(time_window, page)
        
        if data is None:
            return Response(
                {'error': 'Failed to fetch trending movies'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Add context for favorites checking
        for movie in data.get('results', []):
            movie['is_favorite'] = False
            if request.user.is_authenticated:
                movie['is_favorite'] = UserFavorite.objects.filter(
                    user=request.user,
                    movie__tmdb_id=movie['id']
                ).exists()
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class PopularMoviesView(generics.ListAPIView):
    """API endpoint for fetching popular movies from TMDb"""
    permission_classes = [AllowAny]
    serializer_class = TrendingMoviesResponseSerializer  # Same structure
    
    @extend_schema(
        summary="Get popular movies",
        description="Fetch popular movies from TMDb API with caching",
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination",
                default=1
            ),
        ],
        responses={200: TrendingMoviesResponseSerializer}
    )
    def get(self, request, *args, **kwargs):
        page = int(request.query_params.get('page', 1))
        
        data = tmdb_service.get_popular_movies(page)
        
        if data is None:
            return Response(
                {'error': 'Failed to fetch popular movies'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Add context for favorites checking
        for movie in data.get('results', []):
            movie['is_favorite'] = False
            if request.user.is_authenticated:
                movie['is_favorite'] = UserFavorite.objects.filter(
                    user=request.user,
                    movie__tmdb_id=movie['id']
                ).exists()
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class MovieRecommendationsView(generics.ListAPIView):
    """API endpoint for fetching movie recommendations from TMDb"""
    permission_classes = [AllowAny]
    serializer_class = MovieRecommendationsResponseSerializer
    
    @extend_schema(
        summary="Get movie recommendations",
        description="Fetch movie recommendations from TMDb API based on a movie ID",
        parameters=[
            OpenApiParameter(
                name='movie_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="TMDb movie ID to get recommendations for",
                required=True
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination",
                default=1
            ),
        ],
        responses={200: MovieRecommendationsResponseSerializer}
    )
    def get(self, request, *args, **kwargs):
        movie_id = request.query_params.get('movie_id')
        page = int(request.query_params.get('page', 1))
        
        if not movie_id:
            return Response(
                {'error': 'movie_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            movie_id = int(movie_id)
        except ValueError:
            return Response(
                {'error': 'movie_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = tmdb_service.get_movie_recommendations(movie_id, page)
        
        if data is None:
            return Response(
                {'error': 'Failed to fetch movie recommendations'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Add context for favorites checking
        for movie in data.get('results', []):
            movie['is_favorite'] = False
            if request.user.is_authenticated:
                movie['is_favorite'] = UserFavorite.objects.filter(
                    user=request.user,
                    movie__tmdb_id=movie['id']
                ).exists()
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class MovieSearchView(generics.ListAPIView):
    """API endpoint for searching movies"""
    permission_classes = [AllowAny]
    serializer_class = TrendingMoviesResponseSerializer  # Same structure
    
    @extend_schema(
        summary="Search movies",
        description="Search movies by title using TMDb API",
        parameters=[
            OpenApiParameter(
                name='query',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search query for movie titles",
                required=True
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination",
                default=1
            ),
        ],
        responses={200: TrendingMoviesResponseSerializer}
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query')
        page = int(request.query_params.get('page', 1))
        
        if not query:
            return Response(
                {'error': 'query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = tmdb_service.search_movies(query, page)
        
        if data is None:
            return Response(
                {'error': 'Failed to search movies'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Add context for favorites checking
        for movie in data.get('results', []):
            movie['is_favorite'] = False
            if request.user.is_authenticated:
                movie['is_favorite'] = UserFavorite.objects.filter(
                    user=request.user,
                    movie__tmdb_id=movie['id']
                ).exists()
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Movie model (read-only)"""
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['adult', 'original_language']
    search_fields = ['title', 'original_title', 'overview']
    ordering_fields = ['popularity', 'vote_average', 'release_date', 'created_at']
    ordering = ['-popularity']
    
    @extend_schema(
        summary="Sync movie from TMDb",
        description="Sync a specific movie from TMDb API to local database",
        request=OpenApiParameter(
            name='tmdb_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="TMDb movie ID to sync",
            required=True
        )
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def sync_from_tmdb(self, request):
        """Sync a movie from TMDb to local database"""
        tmdb_id = request.data.get('tmdb_id')
        
        if not tmdb_id:
            return Response(
                {'error': 'tmdb_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movie_data = tmdb_service.get_movie_details(tmdb_id)
        
        if not movie_data:
            return Response(
                {'error': 'Failed to fetch movie from TMDb'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        movie = tmdb_service.sync_movie_to_db(movie_data)
        
        if movie:
            serializer = self.get_serializer(movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to sync movie to database'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserFavoriteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user's favorite movies"""
    serializer_class = UserFavoriteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return favorites for the current user only"""
        return UserFavorite.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Add movie to favorites by TMDb ID",
        description="Add a movie to user's favorites by TMDb ID (will sync movie if not exists)",
    )
    @action(detail=False, methods=['post'])
    def add_by_tmdb_id(self, request):
        """Add a movie to favorites by TMDb ID"""
        tmdb_id = request.data.get('tmdb_id')
        
        if not tmdb_id:
            return Response(
                {'error': 'tmdb_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tmdb_id = int(tmdb_id)
        except ValueError:
            return Response(
                {'error': 'tmdb_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if movie exists in database
        try:
            movie = Movie.objects.get(tmdb_id=tmdb_id)
        except Movie.DoesNotExist:
            # Sync movie from TMDb
            movie_data = tmdb_service.get_movie_details(tmdb_id)
            if not movie_data:
                return Response(
                    {'error': 'Movie not found in TMDb'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            movie = tmdb_service.sync_movie_to_db(movie_data)
            if not movie:
                return Response(
                    {'error': 'Failed to sync movie from TMDb'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Check if already in favorites
        favorite, created = UserFavorite.objects.get_or_create(
            user=request.user,
            movie=movie
        )
        
        if not created:
            return Response(
                {'message': 'Movie already in favorites'},
                status=status.HTTP_200_OK
            )
        
        serializer = self.get_serializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Remove movie from favorites by TMDb ID",
        description="Remove a movie from user's favorites by TMDb ID",
    )
    @action(detail=False, methods=['delete'])
    def remove_by_tmdb_id(self, request):
        """Remove a movie from favorites by TMDb ID"""
        tmdb_id = request.data.get('tmdb_id')
        
        if not tmdb_id:
            return Response(
                {'error': 'tmdb_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tmdb_id = int(tmdb_id)
        except ValueError:
            return Response(
                {'error': 'tmdb_id must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            favorite = UserFavorite.objects.get(
                user=request.user,
                movie__tmdb_id=tmdb_id
            )
            favorite.delete()
            return Response(
                {'message': 'Movie removed from favorites'},
                status=status.HTTP_204_NO_CONTENT
            )
        except UserFavorite.DoesNotExist:
            return Response(
                {'error': 'Movie not in favorites'},
                status=status.HTTP_404_NOT_FOUND
            )
