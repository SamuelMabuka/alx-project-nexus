from django.contrib import admin
from .models import Movie, Genre, MovieGenre, UserFavorite


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'tmdb_id']
    search_fields = ['name']
    ordering = ['name']


class MovieGenreInline(admin.TabularInline):
    model = MovieGenre
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'popularity', 'vote_average', 'created_at']
    list_filter = ['adult', 'original_language', 'release_date']
    search_fields = ['title', 'original_title', 'overview']
    ordering = ['-popularity']
    readonly_fields = ['tmdb_id', 'created_at', 'updated_at']
    inlines = [MovieGenreInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tmdb_id', 'title', 'original_title', 'overview')
        }),
        ('Media', {
            'fields': ('poster_path', 'backdrop_path')
        }),
        ('Details', {
            'fields': ('release_date', 'adult', 'original_language')
        }),
        ('Statistics', {
            'fields': ('popularity', 'vote_average', 'vote_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'movie__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
