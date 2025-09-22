from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    """Model for storing movie data from TMDb API"""
    tmdb_id = models.IntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True, blank=True)
    adult = models.BooleanField(default=False)
    original_language = models.CharField(max_length=10, blank=True)
    popularity = models.FloatField(default=0.0)
    vote_average = models.FloatField(default=0.0)
    vote_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['popularity']),
            models.Index(fields=['vote_average']),
            models.Index(fields=['release_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.release_date.year if self.release_date else 'N/A'})"


class Genre(models.Model):
    """Model for movie genres"""
    tmdb_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class MovieGenre(models.Model):
    """Many-to-many relationship between movies and genres"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_genres')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='genre_movies')
    
    class Meta:
        unique_together = ('movie', 'genre')


class UserFavorite(models.Model):
    """Model for storing user's favorite movies"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.movie.title}"
