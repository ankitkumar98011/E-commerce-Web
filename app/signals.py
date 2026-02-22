"""
Auto-train the ML model when products are added/modified
Uses Django signals to trigger training
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management import call_command
from app.models import Product
import threading

@receiver(post_save, sender=Product)
def auto_train_model_on_product_change(sender, instance, created, **kwargs):
    """
    Automatically retrain the ML model when a product is created/updated
    Runs in background to avoid blocking the request
    """
    if created:
        # Only train on new products, not every update
        def train_in_background():
            try:
                print("🔄 Auto-training ML model due to new product...")
                call_command('train_ml_model', '--source', 'database')
            except Exception as e:
                print(f"⚠️  Auto-training failed: {e}")
        
        # Start training in background thread
        thread = threading.Thread(target=train_in_background, daemon=True)
        thread.start()
