from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer
import logging

logger = logging.getLogger(__name__)

class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    Creates a new user account with email, password, and profile information.
    Returns the created user data (without password) and JWT tokens.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can register
    
    @extend_schema(
        summary="Register New User",
        description="Create a new user account with email and password",
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Validation errors"),
        }
    )
    def post(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Create the user
            user = serializer.save()
            
            # Generate JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Log successful registration
            logger.info(f"New user registered: {user.email}")
            
            # Return user data and tokens
            user_data = UserSerializer(user).data
            
            return Response({
                'message': 'User registered successfully',
                'user': user_data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    
    Authenticates user with email/password and returns JWT tokens.
    Extends the default JWT login view to use email instead of username.
    """
    
    @extend_schema(
        summary="User Login",
        description="Authenticate user and return JWT tokens",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful"),
            401: OpenApiResponse(description="Invalid credentials"),
        }
    )
    def post(self, request, *args, **kwargs):
        """Handle user login."""
        login_serializer = LoginSerializer(data=request.data)
        
        if login_serializer.is_valid():
            user = login_serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Send login signal (updates last_login)
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            
            # Log successful login
            logger.info(f"User logged in: {user.email}")
            
            # Return user data and tokens
            user_data = UserSerializer(user).data
            
            return Response({
                'message': 'Login successful',
                'user': user_data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(login_serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile management.
    
    GET: Retrieve current user's profile
    PUT: Update current user's profile
    PATCH: Partially update current user's profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Must be logged in
    
    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user
    
    @extend_schema(
        summary="Get User Profile",
        description="Retrieve the current user's profile information",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def get(self, request, *args, **kwargs):
        """Get current user's profile."""
        user = self.get_object()
        serializer = self.get_serializer(user)
        
        logger.info(f"Profile viewed: {user.email}")
        
        return Response({
            'message': 'Profile retrieved successfully',
            'user': serializer.data
        })
    
    @extend_schema(
        summary="Update User Profile",
        description="Update the current user's profile information",
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def put(self, request, *args, **kwargs):
        """Update user profile (full update)."""
        return self._update_profile(request, partial=False)
    
    @extend_schema(
        summary="Partially Update User Profile",
        description="Partially update the current user's profile information",
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Validation errors"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update user profile (partial update)."""
        return self._update_profile(request, partial=True)
    
    def _update_profile(self, request, partial=False):
        """Helper method to update user profile."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            
            logger.info(f"Profile updated: {user.email}")
            
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    """
    API endpoint for user logout.
    
    Blacklists the provided refresh token to prevent further use.
    This effectively logs out the user from this session.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="User Logout",
        description="Logout user by blacklisting refresh token",
        request={
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'description': 'Refresh token to blacklist'}
            }
        },
        responses={
            200: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Invalid token"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def post(self, request):
        """Handle user logout."""
        try:
            refresh_token = request.data.get("refresh")
            
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Blacklist the token
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error for {request.user.email}: {str(e)}")
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class TokenRefreshView(TokenRefreshView):
    """
    API endpoint for refreshing JWT access tokens.
    
    Takes a refresh token and returns a new access token.
    Extends the default JWT refresh view with custom logging.
    """
    
    @extend_schema(
        summary="Refresh JWT Token",
        description="Get a new access token using refresh token",
        responses={
            200: OpenApiResponse(description="Token refreshed successfully"),
            401: OpenApiResponse(description="Invalid refresh token"),
        }
    )
    def post(self, request, *args, **kwargs):
        """Handle token refresh."""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            logger.info("JWT token refreshed successfully")
        
        return response

# Additional utility views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    Get user statistics and activity summary.
    
    Returns information like account creation date, last login, etc.
    """
    user = request.user
    
    stats = {
        'user_id': user.id,
        'email': user.email,
        'full_name': user.get_full_name(),
        'account_created': user.date_joined,
        'last_login': user.last_login,
        'is_active': user.is_active,
        'age': user.age,
    }
    
    return Response({
        'message': 'User statistics retrieved',
        'stats': stats
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change user password.
    
    Requires current password for verification and new password.
    """
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not current_password or not new_password:
        return Response(
            {'error': 'Both current_password and new_password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check current password
    if not user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new password
    try:
        from django.contrib.auth.password_validation import validate_password
        validate_password(new_password, user)
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Change password
    user.set_password(new_password)
    user.save()
    
    logger.info(f"Password changed for user: {user.email}")
    
    return Response({
        'message': 'Password changed successfully'
    })
