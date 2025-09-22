from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
from .models import Movie, Genre, UserFavorite
from .services import tmdb_service


class MovieModelTest(TestCase):
    """Test Movie model"""
    
    def setUp(self):
        self.movie = Movie.objects.create(
            tmdb_id=12345,
            title="Test Movie",
            original_title="Test Movie Original",
            overview="A test movie for testing",
            popularity=8.5,
            vote_average=7.8,
            vote_count=1000
        )
    
    def test_movie_str_representation(self):
        """Test movie string representation"""
        self.assertEqual(str(self.movie), "Test Movie (N/A)")
    
    def test_movie_creation(self):
        """Test movie creation with required fields"""
        self.assertEqual(self.movie.tmdb_id, 12345)
        self.assertEqual(self.movie.title, "Test Movie")
        self.assertEqual(self.movie.popularity, 8.5)


class GenreModelTest(TestCase):
    """Test Genre model"""
    
    def setUp(self):
        self.genre = Genre.objects.create(
            tmdb_id=28,
            name="Action"
        )
    
    def test_genre_str_representation(self):
        """Test genre string representation"""
        self.assertEqual(str(self.genre), "Action")


class UserFavoriteModelTest(TestCase):
    """Test UserFavorite model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.movie = Movie.objects.create(
            tmdb_id=12345,
            title="Test Movie",
            popularity=8.5
        )
        self.favorite = UserFavorite.objects.create(
            user=self.user,
            movie=self.movie
        )
    
    def test_favorite_str_representation(self):
        """Test favorite string representation"""
        self.assertEqual(str(self.favorite), "testuser likes Test Movie")
    
    def test_unique_constraint(self):
        """Test that user can't favorite the same movie twice"""
        with self.assertRaises(Exception):
            UserFavorite.objects.create(
                user=self.user,
                movie=self.movie
            )


class TMDbServiceTest(TestCase):
    """Test TMDb API service"""
    
    @patch('movies.services.cache.get')
    @patch('movies.services.cache.set')
    @patch('movies.services.requests.Session.get')
    def test_get_trending_movies(self, mock_get, mock_cache_set, mock_cache_get):
        """Test fetching trending movies"""
        mock_cache_get.return_value = None  # No cached data
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'page': 1,
            'results': [
                {
                    'id': 12345,
                    'title': 'Test Movie',
                    'popularity': 8.5
                }
            ],
            'total_pages': 1,
            'total_results': 1
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = tmdb_service.get_trending_movies()
        
        self.assertIsNotNone(result)
        self.assertEqual(result['page'], 1)
        self.assertEqual(len(result['results']), 1)
        mock_cache_set.assert_called_once()
    
    @patch('movies.services.cache.get')
    @patch('movies.services.requests.Session.get')
    def test_api_request_failure(self, mock_get, mock_cache_get):
        """Test API request failure handling"""
        mock_cache_get.return_value = None  # No cached data
        mock_get.side_effect = Exception("API Error")
        
        result = tmdb_service.get_trending_movies()
        
        self.assertIsNone(result)


class AuthenticationAPITest(APITestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')
        self.profile_url = reverse('profile')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_jwt_token_obtain(self):
        """Test JWT token obtain"""
        user = User.objects.create_user(**self.user_data)
        
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.token_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh"""
        user = User.objects.create_user(**self.user_data)
        refresh = RefreshToken.for_user(user)
        
        refresh_data = {'refresh': str(refresh)}
        response = self.client.post(self.refresh_url, refresh_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_user_profile_authenticated(self):
        """Test user profile access with authentication"""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_user_profile_unauthenticated(self):
        """Test user profile access without authentication"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MovieAPITest(APITestCase):
    """Test movie API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.movie = Movie.objects.create(
            tmdb_id=12345,
            title="Test Movie",
            popularity=8.5,
            vote_average=7.8,
            vote_count=1000
        )
        
        self.trending_url = reverse('trending-movies')
        self.popular_url = reverse('popular-movies')
        self.recommendations_url = reverse('movie-recommendations')
        self.search_url = reverse('movie-search')
    
    @patch('movies.views.tmdb_service.get_trending_movies')
    def test_trending_movies_endpoint(self, mock_trending):
        """Test trending movies endpoint"""
        mock_trending.return_value = {
            'page': 1,
            'results': [
                {
                    'id': 12345,
                    'title': 'Test Movie',
                    'popularity': 8.5
                }
            ],
            'total_pages': 1,
            'total_results': 1
        }
        
        response = self.client.get(self.trending_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    @patch('movies.views.tmdb_service.get_popular_movies')
    def test_popular_movies_endpoint(self, mock_popular):
        """Test popular movies endpoint"""
        mock_popular.return_value = {
            'page': 1,
            'results': [
                {
                    'id': 12345,
                    'title': 'Test Movie',
                    'popularity': 8.5
                }
            ],
            'total_pages': 1,
            'total_results': 1
        }
        
        response = self.client.get(self.popular_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    @patch('movies.views.tmdb_service.get_movie_recommendations')
    def test_recommendations_endpoint(self, mock_recommendations):
        """Test movie recommendations endpoint"""
        mock_recommendations.return_value = {
            'page': 1,
            'results': [
                {
                    'id': 67890,
                    'title': 'Recommended Movie',
                    'popularity': 7.5
                }
            ],
            'total_pages': 1,
            'total_results': 1
        }
        
        response = self.client.get(self.recommendations_url, {'movie_id': 12345})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_recommendations_endpoint_missing_movie_id(self):
        """Test recommendations endpoint without movie_id"""
        response = self.client.get(self.recommendations_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('movies.views.tmdb_service.search_movies')
    def test_search_movies_endpoint(self, mock_search):
        """Test movie search endpoint"""
        mock_search.return_value = {
            'page': 1,
            'results': [
                {
                    'id': 12345,
                    'title': 'Test Movie',
                    'popularity': 8.5
                }
            ],
            'total_pages': 1,
            'total_results': 1
        }
        
        response = self.client.get(self.search_url, {'query': 'test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_search_movies_endpoint_missing_query(self):
        """Test search endpoint without query"""
        response = self.client.get(self.search_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserFavoriteAPITest(APITestCase):
    """Test user favorites API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.movie = Movie.objects.create(
            tmdb_id=12345,
            title="Test Movie",
            popularity=8.5
        )
        
        self.favorites_url = reverse('userfavorite-list')
        self.add_by_tmdb_url = reverse('userfavorite-add-by-tmdb-id')
        self.remove_by_tmdb_url = reverse('userfavorite-remove-by-tmdb-id')
    
    def test_favorites_list_authenticated(self):
        """Test favorites list for authenticated user"""
        self.client.force_authenticate(user=self.user)
        UserFavorite.objects.create(user=self.user, movie=self.movie)
        
        response = self.client.get(self.favorites_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_favorites_list_unauthenticated(self):
        """Test favorites list without authentication"""
        response = self.client.get(self.favorites_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_favorite_by_tmdb_id(self):
        """Test adding favorite by TMDb ID"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.add_by_tmdb_url,
            {'tmdb_id': 12345}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserFavorite.objects.filter(
                user=self.user,
                movie__tmdb_id=12345
            ).exists()
        )
    
    def test_add_favorite_duplicate(self):
        """Test adding duplicate favorite"""
        self.client.force_authenticate(user=self.user)
        UserFavorite.objects.create(user=self.user, movie=self.movie)
        
        response = self.client.post(
            self.add_by_tmdb_url,
            {'tmdb_id': 12345}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('already in favorites', response.data['message'])
    
    def test_remove_favorite_by_tmdb_id(self):
        """Test removing favorite by TMDb ID"""
        self.client.force_authenticate(user=self.user)
        UserFavorite.objects.create(user=self.user, movie=self.movie)
        
        response = self.client.delete(
            self.remove_by_tmdb_url,
            {'tmdb_id': 12345}
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            UserFavorite.objects.filter(
                user=self.user,
                movie__tmdb_id=12345
            ).exists()
        )
    
    def test_remove_nonexistent_favorite(self):
        """Test removing non-existent favorite"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(
            self.remove_by_tmdb_url,
            {'tmdb_id': 99999}
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('not in favorites', response.data['error'])
