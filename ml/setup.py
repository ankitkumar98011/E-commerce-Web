"""
Quick setup and training guide for ML system
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ml.recommendation import recommendation_engine
from ml.evaluate import ModelEvaluator
from app.models import Product

print("\n" + "="*70)
print("  🚀 ML RECOMMENDATION ENGINE - QUICK START")
print("="*70 + "\n")

# Check database
product_count = Product.objects.count()
print(f"📊 Products in Database: {product_count}")

if product_count == 0:
    print("\n⚠️  No products found. Adding sample products...\n")
    # Sample products
    samples = [
        {"name": "Wireless Mouse", "category": "Electronics", "price": 799},
        {"name": "Mechanical Keyboard", "category": "Electronics", "price": 2499},
        {"name": "USB-C Cable", "category": "Electronics", "price": 299},
        {"name": "Monitor Stand", "category": "Electronics", "price": 1599},
        {"name": "Laptop Bag", "category": "Accessories", "price": 1999},
        {"name": "Phone Case", "category": "Accessories", "price": 499},
    ]
    for sample in samples:
        Product.objects.get_or_create(**sample)
    print("✅ Sample products added!\n")

print("\n📚 Step 1: Training the Model")
print("-" * 70)
print("Running initial training from database...\n")

success = recommendation_engine.train_from_database()

if success:
    print("\n✅ Model trained successfully!")
    
    print("\n📈 Step 2: Model Evaluation")
    print("-" * 70)
    ModelEvaluator.print_evaluation()
    
    print("\n🎯 Step 3: Getting Recommendations")
    print("-" * 70)
    
    # Test recommendations
    test_product = Product.objects.first()
    if test_product:
        recs = recommendation_engine.get_recommendations(test_product.id, n_recommendations=3)
        print(f"\n  For product: {test_product.name}")
        print(f"  Recommendations: {recs}")
    
    trending = recommendation_engine.get_trending_products(3)
    print(f"\n  Trending products: {trending}")
    
    print("\n\n" + "="*70)
    print("  ✅ ML SYSTEM READY!")
    print("="*70)
    print("""
  Next Steps:
  
  1. Start Django server:
     python manage.py runserver
     
  2. Visit homepage to see recommendations
  
  3. For auto-training (optional):
     pip install schedule
     python ml/auto_train.py
     
  4. Manual retraining anytime:
     python manage.py train_ml_model
     
  5. View model details:
     python ml/evaluate.py
     
  📚 Full docs in: ml/README.md
  """)
else:
    print("\n❌ Model training failed!")
    print("Please check the error messages above.")

print("\n")
