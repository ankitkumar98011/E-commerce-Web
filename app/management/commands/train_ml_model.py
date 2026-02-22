from django.core.management.base import BaseCommand
from ml.recommendation import recommendation_engine
import time

class Command(BaseCommand):
    help = 'Train the ML recommendation model from database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='database',
            help='Data source: database or csv'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting ML Model Training...\n')
        )
        
        start_time = time.time()
        
        if options['source'] == 'csv':
            success = recommendation_engine.train_from_data("data/transactions.csv")
        else:
            success = recommendation_engine.train_from_database()
        
        elapsed = time.time() - start_time
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Model training completed in {elapsed:.2f}s\n'
                    f'Model saved to: ml/model.pkl'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Model training failed')
            )
