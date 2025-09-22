from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Genre, UserFavorite


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model"""
    
    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    """Serializer for Movie model"""
    genres = serializers.SerializerMethodField()
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'original_title', 'overview',
            'poster_path', 'poster_url', 'backdrop_path', 'backdrop_url',
            'release_date', 'adult', 'original_language', 'popularity',
            'vote_average', 'vote_count', 'genres', 'is_favorite'
        ]
    
    def get_genres(self, obj):
        """Get list of genres for the movie"""
        genres = Genre.objects.filter(genre_movies__movie=obj)
        return GenreSerializer(genres, many=True).data
    
    def get_poster_url(self, obj):
        """Get full URL for poster image"""
        if obj.poster_path:
            return f"https://image.tmdb.org/t/p/w500{obj.poster_path}"
        return None
    
    def get_backdrop_url(self, obj):
        """Get full URL for backdrop image"""
        if obj.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{obj.backdrop_path}"
        return None
    
    def get_is_favorite(self, obj):
        """Check if movie is in user's favorites"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavorite.objects.filter(user=request.user, movie=obj).exists()
        return False


class TMDbMovieSerializer(serializers.Serializer):
    """Serializer for movies from TMDb API (not stored in database)"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    original_title = serializers.CharField(required=False, allow_blank=True)
    overview = serializers.CharField(required=False, allow_blank=True)
    poster_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    backdrop_path = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    release_date = serializers.CharField(required=False, allow_blank=True)
    adult = serializers.BooleanField(default=False)
    original_language = serializers.CharField(required=False, allow_blank=True)
    popularity = serializers.FloatField(default=0.0)
    vote_average = serializers.FloatField(default=0.0)
    vote_count = serializers.IntegerField(default=0)
    genre_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    
    def get_poster_url(self, obj):
        """Get full URL for poster image"""
        poster_path = obj.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None
    
    def get_backdrop_url(self, obj):
        """Get full URL for backdrop image"""
        backdrop_path = obj.get('backdrop_path')
        if backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
        return None
    
    def get_is_favorite(self, obj):
        """Check if movie is in user's favorites"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            tmdb_id = obj.get('id')
            if tmdb_id:
                return UserFavorite.objects.filter(
                    user=request.user, 
                    movie__tmdb_id=tmdb_id
                ).exists()
        return False


class UserFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for UserFavorite model"""
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserFavorite
        fields = ['id', 'movie', 'movie_id', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        """Create user favorite with automatic user assignment"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_movie_id(self, value):
        """Validate that the movie exists"""
        try:
            Movie.objects.get(id=value)
        except Movie.DoesNotExist:
            raise serializers.ValidationError("Movie not found.")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        """Create user with encrypted password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TrendingMoviesResponseSerializer(serializers.Serializer):
    """Serializer for trending movies API response"""
    page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_results = serializers.IntegerField()
    results = TMDbMovieSerializer(many=True)


class MovieRecommendationsResponseSerializer(serializers.Serializer):
    """Serializer for movie recommendations API response"""
    page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_results = serializers.IntegerField()
    results = TMDbMovieSerializer(many=True)