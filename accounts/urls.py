# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    UserLogoutView,
    TokenRefreshView,
    user_stats,
    change_password
)

# Define URL patterns for the accounts app
urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    
    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User profile management
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('stats/', user_stats, name='user-stats'),
    path('change-password/', change_password, name='change-password'),
]

"""
URL Mapping Summary:
=====================

POST /api/auth/register/         → Register new user
POST /api/auth/login/            → User login (get JWT tokens)
POST /api/auth/logout/           → User logout (blacklist token)
POST /api/auth/token/refresh/    → Refresh JWT access token

GET  /api/auth/profile/          → Get current user profile
PUT  /api/auth/profile/          → Update user profile (full)
PATCH /api/auth/profile/         → Update user profile (partial)

GET  /api/auth/stats/            → Get user account statistics  
POST /api/auth/change-password/  → Change user password

Authentication Required:
- All endpoints except register/ and login/ require JWT token
- Token should be sent in Authorization header: "Bearer <access_token>"

Example Usage:
- Register: POST /api/auth/register/ with user data
- Login: POST /api/auth/login/ with email/password
- Profile: GET /api/auth/profile/ with Authorization header
"""