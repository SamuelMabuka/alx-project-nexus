# Create: accounts/management/commands/ensure_superuser.py
# filepath: d:\ALX\nexus\accounts\management\commands\ensure_superuser.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Ensure superuser exists for Render deployment'

    def handle(self, *args, **options):
        email = 'admin@nexusmovies.com'
        password = 'NexusRender2024!'
        first_name = 'Nexus'
        last_name = 'Admin'
        
        try:
            # Check if any superuser exists
            if not User.objects.filter(is_superuser=True).exists():
                # Create superuser with explicit field mapping
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Superuser created successfully!')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'📧 Email: {email}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'🔐 Password: {password}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'👤 Name: {first_name} {last_name}')
                )
            else:
                existing = User.objects.filter(is_superuser=True).first()
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Superuser already exists: {existing.email}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating superuser: {str(e)}')
            )
            # Log the full error for debugging
            import traceback
            self.stdout.write(
                self.style.ERROR(f'Full error: {traceback.format_exc()}')
            )