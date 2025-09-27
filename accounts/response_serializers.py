# Create accounts/response_serializers.py
# filepath: d:\ALX\nexus\accounts\response_serializers.py

from rest_framework import serializers

class SuccessMessageSerializer(serializers.Serializer):
    """Serializer for success response messages."""
    message = serializers.CharField(
        help_text="Success message describing the operation result"
    )

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    error = serializers.CharField(
        help_text="Error message describing what went wrong"
    )

class ValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation error responses."""
    message = serializers.CharField(
        help_text="General error message",
        required=False
    )
    errors = serializers.DictField(
        help_text="Field-specific validation errors",
        required=False
    )

class TokenResponseSerializer(serializers.Serializer):
    """Serializer for JWT token responses."""
    access = serializers.CharField(
        help_text="JWT access token for API authentication"
    )
    refresh = serializers.CharField(
        help_text="JWT refresh token for obtaining new access tokens"
    )

class UserDataSerializer(serializers.Serializer):
    """Serializer for user data in responses."""
    id = serializers.IntegerField(
        help_text="User ID"
    )
    email = serializers.EmailField(
        help_text="User email address"
    )
    first_name = serializers.CharField(
        help_text="User first name"
    )
    last_name = serializers.CharField(
        help_text="User last name"
    )

class LoginSuccessSerializer(serializers.Serializer):
    """Serializer for successful login response."""
    message = serializers.CharField(
        help_text="Success message",
        default="User created successfully"
    )
    access = serializers.CharField(
        help_text="JWT access token"
    )
    refresh = serializers.CharField(
        help_text="JWT refresh token"
    )
    user = UserDataSerializer(
        help_text="User information"
    )

class ProfileUpdateSuccessSerializer(serializers.Serializer):
    """Serializer for successful profile update response."""
    message = serializers.CharField(
        help_text="Success message",
        default="Profile updated successfully"
    )
    user = UserDataSerializer(
        help_text="Updated user information"
    )