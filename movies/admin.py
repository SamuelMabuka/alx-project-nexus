from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Movie, Favorite, Rating, Watchlist, UserPreference

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Admin interface for Genre model."""
    
    list_display = ('name', 'tmdb_id', 'movie_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin interface for Movie model."""
    
    list_display = (
        'title', 'release_year', 'vote_average', 'popularity',
        'poster_thumbnail', 'genre_list', 'is_active'
    )
    list_filter = (
        'is_active', 'adult', 'status', 'original_language',
        'release_date', 'genres'
    )
    search_fields = ('title', 'original_title', 'overview', 'tmdb_id')
    list_editable = ('is_active',)
    ordering = ('-popularity', '-vote_average')
    readonly_fields = ('created_at', 'updated_at', 'last_updated_from_tmdb')
    filter_horizontal = ('genres',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'original_title', 'tmdb_id', 'overview', 'tagline')
        }),
        ('Release & Runtime', {
            'fields': ('release_date', 'runtime', 'status')
        }),
        ('Ratings & Popularity', {
            'fields': ('vote_average', 'vote_count', 'popularity')
        }),
        ('Images', {
            'fields': ('poster_path', 'backdrop_path'),
            'classes': ('collapse',)
        }),
        ('Financial', {
            'fields': ('budget', 'revenue'),
            'classes': ('collapse',)
        }),
        ('Language & Location', {
            'fields': (
                'original_language', 'production_countries', 
                'spoken_languages'
            ),
            'classes': ('collapse',)
        }),
        ('Relationships', {
            'fields': ('genres',)
        }),
        ('Settings', {
            'fields': ('adult', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_updated_from_tmdb'),
            'classes': ('collapse',)
        }),
    )
    
    def poster_thumbnail(self, obj):
        """Display poster thumbnail in admin."""
        if obj.poster_url:
            return format_html(
                '<img src="{}" style="height: 60px; width: auto;" />',
                obj.poster_url
            )
        return "No image"
    poster_thumbnail.short_description = "Poster"

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin interface for Favorite model."""
    
    list_display = ('user', 'movie', 'created_at')
    list_filter = ('created_at', 'movie__genres')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'movie__title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Admin interface for Rating model."""
    
    list_display = ('user', 'movie', 'rating_display', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'movie__genres')
    search_fields = ('user__email', 'movie__title', 'review')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    """Admin interface for Watchlist model."""
    
    list_display = ('user', 'movie', 'priority', 'created_at')
    list_filter = ('priority', 'created_at', 'movie__genres')
    search_fields = ('user__email', 'movie__title', 'notes')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for UserPreference model."""
    
    list_display = (
        'user', 'min_rating', 'preferred_decade', 
        'include_adult', 'favorite_genre_names'
    )
    list_filter = ('preferred_decade', 'include_adult', 'min_rating')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('favorite_genres',)
    readonly_fields = ('created_at', 'updated_at')
