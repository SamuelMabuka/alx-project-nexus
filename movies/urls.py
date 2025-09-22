from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TrendingMoviesView,
    PopularMoviesView,
    MovieRecommendationsView,
    MovieSearchView,
    MovieViewSet,
    UserFavoriteViewSet,
)

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'favorites', UserFavoriteViewSet, basename='userfavorite')

urlpatterns = [
    # TMDb API endpoints
    path('trending/', TrendingMoviesView.as_view(), name='trending-movies'),
    path('popular/', PopularMoviesView.as_view(), name='popular-movies'),
    path('recommendations/', MovieRecommendationsView.as_view(), name='movie-recommendations'),
    path('search/', MovieSearchView.as_view(), name='movie-search'),
    
    # Router URLs
    path('', include(router.urls)),
]