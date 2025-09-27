from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

# Get the custom User model
User = get_user_model()

class Genre(models.Model):
    """
    Movie genres from TMDb API.
    
    Stores genre information like 'Action', 'Comedy', 'Drama', etc.
    Used for movie categorization and user preference matching.
    """
    
    # TMDb genre ID (unique identifier from TMDb API)
    tmdb_id = models.IntegerField(unique=True, help_text="TMDb Genre ID")
    
    # Genre name (e.g., "Action", "Comedy", "Drama")
    name = models.CharField(max_length=100, help_text="Genre name")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def movie_count(self):
        """Return the number of movies in this genre."""
        return self.movies.count()

class Movie(models.Model):
    """
    Movie model that caches data from TMDb API.
    
    Stores essential movie information locally to reduce API calls
    and improve performance. Updated periodically from TMDb.
    """
    
    # TMDb movie ID (unique identifier from TMDb API)
    tmdb_id = models.IntegerField(unique=True, db_index=True, help_text="TMDb Movie ID")
    
    # Basic movie information
    title = models.CharField(max_length=255, help_text="Movie title")
    original_title = models.CharField(max_length=255, blank=True, help_text="Original title in native language")
    overview = models.TextField(blank=True, help_text="Movie plot summary")
    tagline = models.CharField(max_length=255, blank=True, help_text="Movie tagline")
    
    # Release information
    release_date = models.DateField(null=True, blank=True, help_text="Movie release date")
    runtime = models.PositiveIntegerField(null=True, blank=True, help_text="Runtime in minutes")
    
    # Ratings and popularity
    vote_average = models.FloatField(
        default=0.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Average rating from TMDb (0-10)"
    )
    vote_count = models.PositiveIntegerField(default=0, help_text="Number of votes on TMDb")
    popularity = models.FloatField(default=0.0, help_text="Popularity score from TMDb")
    
    # Images
    poster_path = models.CharField(max_length=255, blank=True, help_text="TMDb poster image path")
    backdrop_path = models.CharField(max_length=255, blank=True, help_text="TMDb backdrop image path")
    
    # Movie details
    budget = models.BigIntegerField(null=True, blank=True, help_text="Movie budget in USD")
    revenue = models.BigIntegerField(null=True, blank=True, help_text="Movie revenue in USD")
    imdb_id = models.CharField(max_length=20, blank=True, help_text="IMDb ID")
    
    # Language and country
    original_language = models.CharField(max_length=10, default='en', help_text="Original language code")
    production_countries = models.JSONField(default=list, blank=True, help_text="List of production countries")
    spoken_languages = models.JSONField(default=list, blank=True, help_text="List of spoken languages")
    
    # Status
    status = models.CharField(max_length=20, default='Released', help_text="Movie status (Released, In Production, etc.)")
    adult = models.BooleanField(default=False, help_text="Adult content flag")
    
    # Relationships
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True, help_text="Movie genres")
    
    # Cache management
    last_updated_from_tmdb = models.DateTimeField(auto_now_add=True, help_text="Last sync with TMDb")
    is_active = models.BooleanField(default=True, help_text="Movie is available")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        ordering = ['-popularity', '-vote_average']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['release_date']),
            models.Index(fields=['vote_average']),
            models.Index(fields=['popularity']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.release_year})"
    
    @property
    def release_year(self):
        """Return the release year."""
        return self.release_date.year if self.release_date else 'Unknown'
    
    @property
    def poster_url(self):
        """Return full poster URL."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None
    
    @property
    def backdrop_url(self):
        """Return full backdrop URL."""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{self.backdrop_path}"
        return None
    
    @property
    def rating_percentage(self):
        """Return rating as percentage (0-100)."""
        return round(self.vote_average * 10, 1)
    
    @property
    def genre_list(self):
        """Return comma-separated genre names."""
        return ", ".join([genre.name for genre in self.genres.all()])
    
    def is_cache_expired(self, days=7):
        """Check if movie data cache is expired."""
        from datetime import timedelta
        expire_date = self.last_updated_from_tmdb + timedelta(days=days)
        return timezone.now() > expire_date

class Favorite(models.Model):
    """
    User's favorite movies.
    
    Tracks which movies users have marked as favorites.
    Used for personalized recommendations and user profiles.
    """
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        unique_together = ('user', 'movie')  # Prevent duplicate favorites
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ♥ {self.movie.title}"

class Rating(models.Model):
    """
    User movie ratings.
    
    Allows users to rate movies from 1-5 stars.
    Used for personalized recommendations and movie scoring.
    """
    
    RATING_CHOICES = [
        (1, '★☆☆☆☆ (1 star)'),
        (2, '★★☆☆☆ (2 stars)'),
        (3, '★★★☆☆ (3 stars)'),
        (4, '★★★★☆ (4 stars)'),
        (5, '★★★★★ (5 stars)'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_ratings')
    
    # Rating value (1-5 stars)
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1-5 stars"
    )
    
    # Optional review text
    review = models.TextField(blank=True, max_length=1000, help_text="Optional written review")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        unique_together = ('user', 'movie')  # One rating per user per movie
        ordering = ['-created_at']
    
    def __str__(self):
        stars = '★' * self.rating + '☆' * (5 - self.rating)
        return f"{self.user.get_full_name()} rated {self.movie.title}: {stars}"
    
    @property
    def rating_display(self):
        """Return rating as stars."""
        return '★' * self.rating + '☆' * (5 - self.rating)

class Watchlist(models.Model):
    """
    User's watchlist (movies to watch later).
    
    Allows users to save movies they want to watch later.
    Separate from favorites for better organization.
    """
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='in_watchlist')
    
    # Optional priority
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Optional notes
    notes = models.TextField(blank=True, max_length=500, help_text="Personal notes about this movie")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Watchlist Item"
        verbose_name_plural = "Watchlist Items"
        unique_together = ('user', 'movie')  # Prevent duplicate watchlist items
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s watchlist: {self.movie.title}"

class UserPreference(models.Model):
    """
    User movie preferences for recommendations.
    
    Stores user preferences like favorite genres, preferred release years,
    minimum rating threshold, etc. Used by recommendation engine.
    """
    
    # Relationships
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='movie_preferences')
    
    # Favorite genres (for recommendations)
    favorite_genres = models.ManyToManyField(Genre, blank=True, help_text="User's preferred genres")
    
    # Preferences
    min_rating = models.FloatField(
        default=6.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Minimum TMDb rating for recommendations"
    )
    preferred_decade = models.CharField(
        max_length=10, 
        blank=True,
        choices=[
            ('2020s', '2020s'),
            ('2010s', '2010s'),
            ('2000s', '2000s'),
            ('1990s', '1990s'),
            ('1980s', '1980s'),
            ('classic', 'Classic (before 1980)'),
        ],
        help_text="Preferred movie decade"
    )
    include_adult = models.BooleanField(default=False, help_text="Include adult content")
    preferred_languages = models.JSONField(default=list, blank=True, help_text="Preferred movie languages")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s movie preferences"
    
    @property
    def favorite_genre_names(self):
        """Return comma-separated favorite genre names."""
        return ", ".join([genre.name for genre in self.favorite_genres.all()])
