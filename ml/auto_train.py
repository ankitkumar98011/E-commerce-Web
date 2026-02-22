#!/usr/bin/env python
"""
Auto-Training Script
Periodically retrains the ML model and monitors performance
"""

import sys
import os
import time
import schedule

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ml.recommendation import recommendation_engine
from ml.evaluate import ModelEvaluator

def train_job():
    """Training job"""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled training...")
    recommendation_engine.train_from_database()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Training completed!")

def monitor_job():
    """Monitoring job"""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Running model evaluation...")
    ModelEvaluator.print_evaluation()

def start_scheduler():
    """
    Start the auto-training scheduler
    Trains every 6 hours
    Evaluates every 12 hours
    """
    print("\n" + "="*60)
    print("   🤖 ML AUTO-TRAINING SCHEDULER STARTED")
    print("="*60)
    print("\n⏰ Schedule:")
    print("   • Model Training: Every 6 hours")
    print("   • Model Evaluation: Every 12 hours")
    print("\n Press Ctrl+C to stop\n")
    
    # Schedule jobs
    schedule.every(6).hours.do(train_job)
    schedule.every(12).hours.do(monitor_job)
    
    # Do initial training
    train_job()
    
    # Keep scheduler running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n🛑 Scheduler stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in scheduler: {e}")
            time.sleep(60)


if __name__ == "__main__":
    try:
        start_scheduler()
    except ImportError:
        print("⚠️  'schedule' library not installed")
        print("Install with: pip install schedule")
        print("\n💡 Running one-time training instead...")
        recommendation_engine.train_from_database()
