"""
Advanced ML Model Evaluation and Analytics
Provides detailed metrics about recommendations system performance
"""

import pickle
from datetime import datetime, timedelta
from app.models import Product, UserInteraction, User
from django.db.models import Count, Avg, Q


class AdvancedModelEvaluator:
    """Evaluate advanced recommendation model performance"""
    
    @staticmethod
    def load_model(model_path="ml/advanced_model.pkl"):
        """Load trained model"""
        try:
            with open(model_path, "rb") as f:
                data = pickle.load(f)
            return data
        except:
            return None
    
    @staticmethod
    def print_evaluation():
        """Print comprehensive model evaluation report"""
        model_data = AdvancedModelEvaluator.load_model()
        
        print("\n" + "="*70)
        print("  🎯 ADVANCED ML RECOMMENDATION ENGINE - EVALUATION REPORT")
        print("="*70 + "\n")
        
        if not model_data:
            print("❌ No model found. Run: python manage.py train_advanced_model\n")
            return
        
        # Model timestamp
        timestamp = model_data.get('timestamp')
        if timestamp:
            print(f"📅 Model Trained: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # PRODUCTS & USERS METRICS
        print("📊 DATASET METRICS:")
        print("-" * 70)
        
        products_count = len(model_data.get('products_list', []))
        users_count = len(model_data.get('users_list', []))
        
        print(f"   • Total Products: {products_count}")
        print(f"   • Total Users: {users_count}")
        
        # Interaction metrics
        interactions = UserInteraction.objects.all()
        print(f"   • Total Interactions: {interactions.count()}")
        
        # Interaction type breakdown
        interaction_breakdown = interactions.values('interaction_type').annotate(count=Count('id'))
        print(f"\n   Interaction Types:")
        for item in interaction_breakdown:
            print(f"      - {item['interaction_type'].title()}: {item['count']}")
        
        # MATRIX METRICS
        print("\n\n🔢 COLLABORATIVE FILTERING METRICS:")
        print("-" * 70)
        
        user_item_matrix = model_data.get('user_item_matrix')
        if user_item_matrix is not None:
            sparsity = 1 - (user_item_matrix != 0).sum().sum() / (user_item_matrix.shape[0] * user_item_matrix.shape[1])
            coverage = 1 - sparsity
            density = 1 - sparsity
            
            print(f"   • Matrix Shape: {user_item_matrix.shape}")
            print(f"   • Sparsity: {sparsity:.2%} (lower is better)")
            print(f"   • Density: {density:.2%}")
            print(f"   • Coverage: {coverage:.2%}")
            print(f"   • Data Points: {(user_item_matrix != 0).sum().sum()}")
        else:
            print("   ⚠️  No user-item interactions available")
        
        # SIMILARITY METRICS
        print("\n\n🔗 SIMILARITY METRICS:")
        print("-" * 70)
        
        product_sim = model_data.get('product_similarity')
        user_sim = model_data.get('user_similarity')
        
        if product_sim is not None:
            print(f"   • Product Similarity Matrix: {product_sim.shape}")
            print(f"   • Avg Product Similarity: {product_sim.mean():.4f}")
        
        if user_sim is not None:
            print(f"   • User Similarity Matrix: {user_sim.shape}")
            print(f"   • Avg User Similarity: {user_sim.mean():.4f}")
        
        # USER PREFERENCES
        print("\n\n👤 USER PREFERENCES ANALYSIS:")
        print("-" * 70)
        
        user_prefs = model_data.get('user_preferences', {})
        print(f"   • Users with Preferences: {len(user_prefs)}")
        
        if user_prefs:
            # Sample preferences
            sample_count = min(3, len(user_prefs))
            print(f"\n   Sample User Preferences (first {sample_count}):")
            for user_id, prefs in list(user_prefs.items())[:sample_count]:
                print(f"\n      User {user_id}:")
                print(f"         - Preferred Categories: {', '.join(prefs.get('preferred_categories', []))}")
                print(f"         - Avg Price: ${prefs.get('avg_price', 0):.2f}")
                print(f"         - Interactions: {prefs.get('interaction_count', 0)}")
                print(f"         - Avg Rating: {prefs.get('avg_rating', 0):.2f}")
        
        # RECOMMENDATION QUALITY METRICS
        print("\n\n⭐ PRODUCT QUALITY METRICS:")
        print("-" * 70)
        
        products = Product.objects.all()
        avg_rating = products.aggregate(Avg('rating'))['rating__avg'] or 0
        avg_reviews = products.aggregate(Avg('total_reviews'))['total_reviews__avg'] or 0
        
        print(f"   • Avg Product Rating: {avg_rating:.2f}/5.0")
        print(f"   • Avg Reviews per Product: {avg_reviews:.0f}")
        print(f"   • Products with Ratings: {products.filter(rating__gt=0).count()}")
        print(f"   • Products with Reviews: {products.filter(total_reviews__gt=0).count()}")
        
        # RECENT ACTIVITY
        print("\n\n📈 RECENT ACTIVITY (Last 7 Days):")
        print("-" * 70)
        
        week_ago = datetime.now() - timedelta(days=7)
        recent_interactions = interactions.filter(timestamp__gte=week_ago)
        recent_users = recent_interactions.values('user').distinct().count()
        
        print(f"   • Interactions (7 days): {recent_interactions.count()}")
        print(f"   • Active Users (7 days): {recent_users}")
        
        if recent_users > 0:
            avg_interactions = recent_interactions.count() / recent_users
            print(f"   • Avg Interactions/User: {avg_interactions:.2f}")
        
        # MODEL FEATURES
        print("\n\n🎨 MODEL FEATURES:")
        print("-" * 70)
        features = [
            "✓ Hybrid Filtering (Content + Collaborative + Popularity)",
            "✓ User Behavior Tracking (Views, Clicks, Purchases, Ratings)",
            "✓ Cold Start Problem Handling",
            "✓ User Preference Learning",
            "✓ Interaction History Tracking",
            "✓ Weighted Interaction Matrix",
            "✓ User Similarity Computation",
            "✓ Product Similarity Computation"
        ]
        for feature in features:
            print(f"   {feature}")
        
        # NEXT STEPS
        print("\n\n💡 NEXT STEPS:")
        print("-" * 70)
        print("   1. Retrain model regularly: python manage.py train_advanced_model")
        print("   2. Monitor interactions: python manage.py shell")
        print("   3. Test recommendations: /api/hybrid-recommendations/")
        print("   4. Analyze user behavior")
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    AdvancedModelEvaluator.print_evaluation()
