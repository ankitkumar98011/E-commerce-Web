"""
Django management command to train the advanced ML model
Usage: python manage.py train_advanced_model
"""

from django.core.management.base import BaseCommand
from ml.advanced_recommendation import advanced_recommendation_engine
import time


class Command(BaseCommand):
    help = 'Train the advanced ML recommendation model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retrain even if model exists',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Starting Advanced ML Model Training\n'))
        
        start_time = time.time()
        
        success = advanced_recommendation_engine.train_from_database()
        
        elapsed = time.time() - start_time
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Training completed in {elapsed:.2f} seconds')
            )
            self.stdout.write(
                self.style.WARNING('\n📊 Model Info:')
            )
            self.stdout.write(f'   • Products: {len(advanced_recommendation_engine.products_list)}')
            self.stdout.write(f'   • Users: {len(advanced_recommendation_engine.users_list)}')
            self.stdout.write(f'   • Model Path: ml/advanced_model.pkl')
            self.stdout.write('\n')
        else:
            self.stdout.write(
                self.style.ERROR('❌ Training failed. Check logs above.')
            )
