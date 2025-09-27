# movies/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Genre, Movie, Favorite, Rating, Watchlist, UserPreference
from drf_spectacular.utils import extend_schema_field

User = get_user_model()

class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model."""
    
    @extend_schema_field(serializers.IntegerField)
    def movie_count(self, obj) -> int:
        """Get count of movies in this genre."""
        return getattr(obj, 'movie_count', 0)
    
    movie_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name', 'movie_count']
        read_only_fields = ['id', 'movie_count']

class MovieListSerializer(serializers.ModelSerializer):
    """
    Serializer for movie list views (lightweight).
    
    Used for popular movies, trending movies, search results.
    Contains only essential fields for performance.
    """
    
    genres = GenreSerializer(many=True, read_only=True)
    
    @extend_schema_field(serializers.CharField)
    def poster_url(self, obj) -> str:
        """Get full poster URL."""
        return getattr(obj, 'poster_url', '')
    
    @extend_schema_field(serializers.CharField) 
    def backdrop_url(self, obj) -> str:
        """Get full backdrop URL."""
        return getattr(obj, 'backdrop_url', '')
    
    @extend_schema_field(serializers.CharField)
    def release_year(self, obj) -> str:
        """Get release year from release date."""
        return getattr(obj, 'release_year', '')
    
    @extend_schema_field(serializers.FloatField)
    def rating_percentage(self, obj) -> float:
        """Get rating as percentage."""
        return getattr(obj, 'rating_percentage', 0.0)
    
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    release_year = serializers.SerializerMethodField()
    rating_percentage = serializers.SerializerMethodField()
    
    # User-specific fields (only if user is authenticated)
    is_favorited = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'original_title', 'overview',
            'release_date', 'release_year', 'vote_average', 'vote_count',
            'popularity', 'poster_path', 'poster_url', 'backdrop_path', 
            'backdrop_url', 'rating_percentage', 'genres', 'original_language',
            'adult', 'is_favorited', 'user_rating'
        ]
        read_only_fields = [
            'id', 'tmdb_id', 'poster_url', 'backdrop_url', 
            'release_year', 'rating_percentage'
        ]
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_favorited(self, obj) -> bool:
        """Check if current user has favorited this movie."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_rating(self, obj) -> int:
        """Get current user's rating for this movie."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            rating = obj.user_ratings.filter(user=user).first()
            return rating.rating if rating else None
        return None

class MovieDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for movie detail views (comprehensive).
    
    Contains all movie information including financial data,
    production details, and user interactions.
    """
    
    genres = GenreSerializer(many=True, read_only=True)
    
    @extend_schema_field(serializers.CharField)
    def poster_url(self, obj) -> str:
        """Get full poster URL."""
        return getattr(obj, 'poster_url', '')
    
    @extend_schema_field(serializers.CharField)
    def backdrop_url(self, obj) -> str:
        """Get full backdrop URL."""
        return getattr(obj, 'backdrop_url', '')
    
    @extend_schema_field(serializers.CharField)
    def release_year(self, obj) -> str:
        """Get release year from release date."""
        return getattr(obj, 'release_year', '')
    
    @extend_schema_field(serializers.FloatField)
    def rating_percentage(self, obj) -> float:
        """Get rating as percentage."""
        return getattr(obj, 'rating_percentage', 0.0)
    
    @extend_schema_field(serializers.CharField)
    def genre_list(self, obj) -> str:
        """Get comma-separated list of genre names."""
        return getattr(obj, 'genre_list', '')
    
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    release_year = serializers.SerializerMethodField()
    rating_percentage = serializers.SerializerMethodField()
    genre_list = serializers.SerializerMethodField()
    
    # User-specific fields
    is_favorited = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    is_in_watchlist = serializers.SerializerMethodField()
    
    # Statistics
    total_favorites = serializers.SerializerMethodField()
    average_user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            # Basic info
            'id', 'tmdb_id', 'title', 'original_title', 'overview', 'tagline',
            # Release info
            'release_date', 'release_year', 'runtime', 'status',
            # Ratings
            'vote_average', 'vote_count', 'popularity', 'rating_percentage',
            # Images
            'poster_path', 'poster_url', 'backdrop_path', 'backdrop_url',
            # Financial
            'budget', 'revenue',
            # Details
            'imdb_id', 'original_language', 'production_countries', 
            'spoken_languages', 'adult',
            # Relationships
            'genres', 'genre_list',
            # User interactions
            'is_favorited', 'user_rating', 'is_in_watchlist',
            # Statistics
            'total_favorites', 'average_user_rating',
            # Timestamps
            'last_updated_from_tmdb', 'created_at'
        ]
        read_only_fields = [
            'id', 'tmdb_id', 'poster_url', 'backdrop_url', 
            'release_year', 'rating_percentage', 'genre_list',
            'last_updated_from_tmdb', 'created_at'
        ]
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_favorited(self, obj) -> bool:
        """Check if current user has favorited this movie."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_rating(self, obj) -> int:
        """Get current user's rating for this movie."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            rating = obj.user_ratings.filter(user=user).first()
            return RatingSerializer(rating).data if rating else None
        return None
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_in_watchlist(self, obj) -> bool:
        """Check if movie is in user's watchlist."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.in_watchlist.filter(user=user).exists()
        return False
    
    @extend_schema_field(serializers.IntegerField)
    def get_total_favorites(self, obj) -> int:
        """Get total number of users who favorited this movie."""
        return obj.favorited_by.count()
    
    @extend_schema_field(serializers.FloatField)
    def get_average_user_rating(self, obj) -> float:
        """Get average user rating for this movie."""
        ratings = obj.user_ratings.all()
        if ratings:
            avg = sum(r.rating for r in ratings) / len(ratings)
            return round(avg, 1)
        return None

class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for Favorite model."""
    
    movie = MovieListSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'user_email', 'movie', 'created_at']
        read_only_fields = ['id', 'user_email', 'created_at']

class RatingSerializer(serializers.ModelSerializer):
    """Serializer for Rating model."""
    
    movie = MovieListSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    @extend_schema_field(serializers.CharField)
    def rating_display(self, obj) -> str:
        """Get rating as star display."""
        return getattr(obj, 'rating_display', '')
    
    rating_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Rating
        fields = [
            'id', 'user_email', 'movie', 'rating', 'rating_display',
            'review', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'rating_display', 'created_at', 'updated_at']

class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserPreference model."""
    
    favorite_genres = GenreSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    @extend_schema_field(serializers.CharField)
    def favorite_genre_names(self, obj) -> str:
        """Get comma-separated list of favorite genre names."""
        return getattr(obj, 'favorite_genre_names', '')
    
    favorite_genre_names = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'user_email', 'favorite_genres', 'favorite_genre_names',
            'min_rating', 'preferred_decade', 'include_adult', 
            'preferred_languages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'favorite_genre_names', 'created_at', 'updated_at']

class UserPreferenceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user preferences."""
    
    favorite_genre_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of genre IDs"
    )
    
    class Meta:
        model = UserPreference
        fields = [
            'favorite_genre_ids', 'min_rating', 'preferred_decade',
            'include_adult', 'preferred_languages'
        ]
    
    def update(self, instance, validated_data):
        """Update user preferences with genre handling."""
        # Handle favorite genres separately
        favorite_genre_ids = validated_data.pop('favorite_genre_ids', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update favorite genres if provided
        if favorite_genre_ids is not None:
            genres = Genre.objects.filter(id__in=favorite_genre_ids)
            instance.favorite_genres.set(genres)
        
        return instance

# Response serializers for API documentation
class MovieSearchResponseSerializer(serializers.Serializer):
    """Serializer for movie search response."""
    
    results = MovieListSerializer(many=True)
    total_results = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    page = serializers.IntegerField()

class MovieListResponseSerializer(serializers.Serializer):
    """Serializer for paginated movie list response."""
    
    results = MovieListSerializer(many=True)
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    status_code = serializers.IntegerField(required=False)

class SuccessResponseSerializer(serializers.Serializer):
    """Serializer for success responses."""
    
    message = serializers.CharField()
    data = serializers.JSONField(required=False)

class RatingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ratings."""
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Rating
        fields = ['movie_id', 'rating', 'review']

class SimpleToggleSerializer(serializers.Serializer):
    """Simple serializer for toggle operations."""
    movie_id = serializers.IntegerField()

class MovieSearchSerializer(serializers.Serializer):
    """Serializer for movie search parameters."""
    query = serializers.CharField(max_length=200)
    page = serializers.IntegerField(default=1, min_value=1)

class GenreListSerializer(serializers.ModelSerializer):
    """Simple genre serializer for lists."""
    class Meta:
        model = Genre
        fields = ['id', 'name', 'tmdb_id']

class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer for Watchlist model."""
    
    movie = MovieListSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'user_email', 'movie', 'created_at']
        read_only_fields = ['id', 'user_email', 'created_at']

class FavoriteToggleSerializer(serializers.Serializer):
    """Serializer for toggling movie favorites."""
    movie_id = serializers.IntegerField(
        help_text="ID of the movie to add/remove from favorites"
    )
    
    def validate_movie_id(self, value):
        """Validate that the movie exists."""
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value

class WatchlistToggleSerializer(serializers.Serializer):
    """Serializer for toggling movie watchlist."""
    movie_id = serializers.IntegerField(
        help_text="ID of the movie to add/remove from watchlist"
    )
    
    def validate_movie_id(self, value):
        """Validate that the movie exists."""
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value

class MovieStatsSerializer(serializers.Serializer):
    """Serializer for user movie statistics."""
    total_favorites = serializers.IntegerField(help_text="Total number of favorite movies")
    total_ratings = serializers.IntegerField(help_text="Total number of rated movies")
    total_watchlist = serializers.IntegerField(help_text="Total number of watchlist movies")
    average_rating = serializers.FloatField(help_text="Average rating given by user")
    favorite_genres = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of favorite genre names"
    )
    most_watched_decade = serializers.CharField(help_text="Most watched movie decade")
    total_movies_watched = serializers.IntegerField(help_text="Total movies in user's history")

class RecommendationSerializer(serializers.Serializer):
    """Serializer for movie recommendations."""
    movies = MovieListSerializer(many=True)
    recommendation_reason = serializers.CharField(help_text="Why this movie was recommended")
    total_recommendations = serializers.IntegerField(help_text="Total number of recommendations")

class GenreStatsSerializer(serializers.Serializer):
    """Serializer for genre statistics."""
    genre_name = serializers.CharField()
    movie_count = serializers.IntegerField()
    user_rating_count = serializers.IntegerField()
    average_user_rating = serializers.FloatField()

class TMDbMovieSerializer(serializers.Serializer):
    """Serializer for TMDb API movie data."""
    id = serializers.IntegerField()
    title = serializers.CharField()
    original_title = serializers.CharField()
    overview = serializers.CharField()
    release_date = serializers.DateField()
    vote_average = serializers.FloatField()
    vote_count = serializers.IntegerField()
    popularity = serializers.FloatField()
    poster_path = serializers.CharField()
    backdrop_path = serializers.CharField()
    adult = serializers.BooleanField()
    original_language = serializers.CharField()
    genre_ids = serializers.ListField(child=serializers.IntegerField())

class PaginatedMovieResponseSerializer(serializers.Serializer):
    """Serializer for paginated movie responses."""
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = MovieListSerializer(many=True)

class MovieSearchRequestSerializer(serializers.Serializer):
    """Serializer for movie search request parameters."""
    query = serializers.CharField(max_length=200, help_text="Search query")
    page = serializers.IntegerField(default=1, min_value=1, help_text="Page number")
    include_adult = serializers.BooleanField(default=False, help_text="Include adult content")
    year = serializers.IntegerField(required=False, help_text="Filter by release year")

class GenreMoviesSerializer(serializers.Serializer):
    """Serializer for movies by genre."""
    genre = GenreSerializer()
    movies = MovieListSerializer(many=True)
    total_movies = serializers.IntegerField()

class UserActivitySerializer(serializers.Serializer):
    """Serializer for user activity summary."""
    recent_favorites = FavoriteSerializer(many=True)
    recent_ratings = RatingSerializer(many=True)
    recent_watchlist = WatchlistSerializer(many=True)
    activity_summary = serializers.DictField()

class MovieUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating movie information."""
    class Meta:
        model = Movie
        fields = [
            'title', 'original_title', 'overview', 'tagline',
            'release_date', 'runtime', 'status', 'budget', 'revenue',
            'imdb_id', 'original_language', 'production_countries',
            'spoken_languages', 'adult'
        ]

# Validation serializers for common operations
class MovieIdSerializer(serializers.Serializer):
    """Simple serializer for movie ID validation."""
    movie_id = serializers.IntegerField()
    
    def validate_movie_id(self, value):
        """Validate that the movie exists."""
        if not Movie.objects.filter(id=value).exists():
            raise serializers.ValidationError("Movie not found.")
        return value

class BulkMovieActionSerializer(serializers.Serializer):
    """Serializer for bulk movie operations."""
    movie_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of movie IDs"
    )
    action = serializers.ChoiceField(
        choices=['favorite', 'unfavorite', 'add_to_watchlist', 'remove_from_watchlist'],
        help_text="Action to perform on movies"
    )

class MovieFiltersSerializer(serializers.Serializer):
    """Serializer for movie filtering parameters."""
    genre_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Filter by genre IDs"
    )
    min_rating = serializers.FloatField(required=False, min_value=0, max_value=10)
    max_rating = serializers.FloatField(required=False, min_value=0, max_value=10)
    year_from = serializers.IntegerField(required=False)
    year_to = serializers.IntegerField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['popularity', 'release_date', 'vote_average', 'title'],
        default='popularity',
        required=False
    )
    order = serializers.ChoiceField(
        choices=['asc', 'desc'],
        default='desc',
        required=False
    )