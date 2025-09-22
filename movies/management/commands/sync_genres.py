from django.core.management.base import BaseCommand
from movies.services import tmdb_service


class Command(BaseCommand):
    help = 'Sync movie genres from TMDb API to local database'
    
    def handle(self, *args, **options):
        self.stdout.write('Starting genre sync from TMDb...')
        
        try:
            tmdb_service.sync_genres_to_db()
            self.stdout.write(
                self.style.SUCCESS('Successfully synced genres from TMDb!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to sync genres: {e}')
            )