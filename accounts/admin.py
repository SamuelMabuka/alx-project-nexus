from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users in admin"""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')  # Remove 'username'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field completely
        if 'username' in self.fields:
            del self.fields['username']

class CustomUserChangeForm(UserChangeForm):
    """Custom form for changing users in admin"""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')  # Remove 'username'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field completely
        if 'username' in self.fields:
            del self.fields['username']

class CustomUserAdmin(UserAdmin):
    """Custom admin interface for User model"""
    
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    # Remove username from all admin displays
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Fieldsets for user detail view (remove username)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),

    )
    
    # Fieldsets for add user view (remove username)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')},
        ),
    )

# Register the custom user admin
admin.site.register(User, CustomUserAdmin)
