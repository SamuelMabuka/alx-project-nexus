from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema

from movies.serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Register a new user",
        description="Create a new user account with username, email, and password",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message': 'User created successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint"""
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve the current user's profile information",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update the current user's profile information",
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update user profile",
        description="Partially update the current user's profile information",
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with better documentation"""
    
    @extend_schema(
        summary="Obtain JWT token pair",
        description="Get access and refresh tokens by providing username and password",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """Custom JWT token refresh view with better documentation"""
    
    @extend_schema(
        summary="Refresh JWT token",
        description="Get a new access token by providing a valid refresh token",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
