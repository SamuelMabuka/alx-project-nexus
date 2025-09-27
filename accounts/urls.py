# accounts/urls.py
from django.urls import path
from django.http import JsonResponse
from . import views

def auth_info(request):
    """Base authentication info endpoint."""
    return JsonResponse({
        'message': 'Nexus Movie API Authentication',
        'endpoints': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'profile': '/api/auth/profile/',
            'change_password': '/api/auth/change-password/',
            'logout': '/api/auth/logout/'
        },
        'authentication': {
            'type': 'JWT (JSON Web Token)',
            'header': 'Authorization: Bearer <access_token>',
            'note': 'Use /api/auth/login/ to get access and refresh tokens'
        },
        'status': 'available'
    })

# Define URL patterns for the accounts app
urlpatterns = [
    # Base auth info endpoint
    path('', auth_info, name='auth-info'),
    
    # Authentication endpoints
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change-password'),
    path('logout/', views.logout_view, name='logout'),
]

"""
URL Mapping Summary:
=====================

POST /api/auth/register/         → Register new user
POST /api/auth/login/            → User login (get JWT tokens)
POST /api/auth/logout/           → User logout (blacklist token)
    
# Removed token management as it's now handled by CustomTokenObtainPairView

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