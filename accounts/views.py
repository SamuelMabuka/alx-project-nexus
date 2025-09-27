from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer, 
    ChangePasswordSerializer,
    LogoutSerializer,
    CustomTokenObtainPairSerializer
)
from .response_serializers import (
    SuccessMessageSerializer,
    ErrorResponseSerializer,
    ValidationErrorSerializer,
    LoginSuccessSerializer
)

User = get_user_model()

@extend_schema(
    request=UserRegistrationSerializer,
    responses={
        201: LoginSuccessSerializer,
        400: ValidationErrorSerializer
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user account"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User created successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=UserProfileSerializer,
    responses={
        200: UserProfileSerializer,
        400: ValidationErrorSerializer
    },
    tags=['User Profile']
)
@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """Get or update user profile"""
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=ChangePasswordSerializer,
    responses={
        200: SuccessMessageSerializer,
        400: ValidationErrorSerializer
    },
    tags=['User Profile']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        
        # Check old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': ['Wrong password.']}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=LogoutSerializer,
    responses={
        205: SuccessMessageSerializer,
        400: ErrorResponseSerializer
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user by blacklisting refresh token"""
    serializer = LogoutSerializer(data=request.data)
    if serializer.is_valid():
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh_token = serializer.validated_data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view that adds user info to response"""
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        tags=['Authentication'],
        responses={
            200: LoginSuccessSerializer,
            401: ErrorResponseSerializer
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            try:
                email = request.data.get('email')
                user = User.objects.get(email=email)
                response.data['user'] = {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            except User.DoesNotExist:
                pass
        
        return response
