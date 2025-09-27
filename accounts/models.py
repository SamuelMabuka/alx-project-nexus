# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model that extends Django's default User model.
    
    Why extend the default User model?
    - Add movie-specific fields (favorite genres, birth date)
    - Use email for login instead of username
    - Store user preferences for better recommendations
    """
    
    # Use email as the unique identifier instead of username
    email = models.EmailField(unique=True, verbose_name='Email Address')
    
    # Optional user profile information
    first_name = models.CharField(max_length=30, verbose_name='First Name')
    last_name = models.CharField(max_length=30, verbose_name='Last Name')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Date of Birth')
    
    # User preferences for movie recommendations
    bio = models.TextField(max_length=500, blank=True, verbose_name='Bio')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email for login instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the user."""
        return f"{self.email} ({self.get_full_name()})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the first name of the user."""
        return self.first_name
    
    @property
    def age(self):
        """Calculate user's age from date_of_birth."""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
