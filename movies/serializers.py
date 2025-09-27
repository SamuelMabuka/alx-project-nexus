# movies/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Genre, Movie, Favorite, Rating, Watchlist, UserPreference

User = get_user_model()

class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model."""
    
    movie_count = serializers.ReadOnlyField()
    
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
    poster_url = serializers.ReadOnlyField()
    backdrop_url = serializers.ReadOnlyField()
    release_year = serializers.ReadOnlyField()
    rating_percentage = serializers.ReadOnlyField()
    
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
    
    def get_is_favorited(self, obj):
        """Check if current user has favorited this movie."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False
    
    def get_user_rating(self, obj):
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
    poster_url = serializers.ReadOnlyField()
    backdrop_url = serializers.ReadOnlyField()
    release_year = serializers.ReadOnlyField()
    rating_percentage = serializers.ReadOnlyField()
    genre_list = serializers.ReadOnlyField()
    
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
    
    def get_is_favorited(self, obj):
        """Check if current user has favorited this movie."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False
    
    def get_user_rating(self, obj):
        """Get current user's rating for this movie."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            rating = obj.user_ratings.filter(user=user).first()
            return RatingSerializer(rating).data if rating else None
        return None
    
    def get_is_in_watchlist(self, obj):
        """Check if movie is in user's watchlist."""
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.in_watchlist.filter(user=user).exists()
        return False
    
    def get_total_favorites(self, obj):
        """Get total number of users who favorited this movie."""
        return obj.favorited_by.count()
    
    def get_average_user_rating(self, obj):
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
    rating_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Rating
        fields = [
            'id', 'user_email', 'movie', 'rating', 'rating_display',
            'review', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'rating_display', 'created_at', 'updated_at']

class RatingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ratings."""
    
    class Meta:
        model = Rating
        fields = ['rating', 'review']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value

class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer for Watchlist model."""
    
    movie = MovieListSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'user_email', 'movie', 'priority', 'notes', 'created_at']
        read_only_fields = ['id', 'user_email', 'created_at']

class WatchlistCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating watchlist items."""
    
    class Meta:
        model = Watchlist
        fields = ['priority', 'notes']

class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserPreference model."""
    
    favorite_genres = GenreSerializer(many=True, read_only=True)
    favorite_genre_names = serializers.ReadOnlyField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    
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