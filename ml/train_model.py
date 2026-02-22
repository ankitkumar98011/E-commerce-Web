#!/usr/bin/env python
"""
ML Model Training Script
Auto-trains the recommendation engine from database or CSV
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ml.recommendation import recommendation_engine
from ml.evaluate import ModelEvaluator
import time

def train_model(source='database'):
    """
    Train the ML recommendation model
    
    Args:
        source (str): 'database' or 'csv' - training data source
    """
    print("\n" + "="*60)
    print("   🤖 ML RECOMMENDATION ENGINE - TRAINING")
    print("="*60 + "\n")
    
    start_time = time.time()
    
    print(f"📊 Training source: {source.upper()}")
    print(f"⏱️  Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Train model
    if source.lower() == 'csv':
        success = recommendation_engine.train_from_data("data/transactions.csv")
    else:
        success = recommendation_engine.train_from_database()
    
    elapsed = time.time() - start_time
    
    if success:
        print(f"\n✅ Training completed successfully!")
        print(f"⏱️  Time taken: {elapsed:.2f} seconds")
        print(f"💾 Model saved to: ml/model.pkl\n")
        
        # Evaluate model
        print("📈 Model Evaluation:")
        ModelEvaluator.print_evaluation()
        return True
    else:
        print(f"\n❌ Training failed!")
        print(f"⏱️  Time elapsed: {elapsed:.2f} seconds\n")
        return False


if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv) > 1 else 'database'
    train_model(source)
