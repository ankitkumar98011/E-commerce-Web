"""
User Interaction Tracking Utilities
Tracks views, clicks, purchases, ratings etc. for ML model
"""

from django.contrib.auth.models import User
from .models import UserInteraction, Product
from datetime import datetime

def track_user_interaction(user, product, interaction_type='view', rating_value=None, session_id=None):
    """
    Track a user's interaction with a product
    
    Args:
        user: User object or None (for anonymous)
        product: Product object
        interaction_type: 'view', 'click', 'purchase', 'rating', 'cart', 'wishlist'
        rating_value: Rating value (1-5) if interaction is rating
        session_id: Session identifier for tracking
    """
    try:
        if user and user.is_authenticated:
            interaction = UserInteraction.objects.create(
                user=user,
                product=product,
                interaction_type=interaction_type,
                rating_value=rating_value,
                session_id=session_id or ''
            )
            return interaction
    except Exception as e:
        print(f"Tracking error: {e}")
        return None

def get_user_session_id(request):
    """Get or create session ID for tracking"""
    session_id = request.session.get('session_id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        request.session['session_id'] = session_id
    return session_id

def get_similar_products(product_id, n=5):
    """Get similar products based on category and price"""
    try:
        product = Product.objects.get(id=product_id)
        
        similar = Product.objects.filter(
            category=product.category
        ).exclude(id=product_id).order_by('-rating', '-total_reviews')[:n]
        
        return list(similar)
    except Product.DoesNotExist:
        return []
    except Exception as e:
        print(f"Similar products error: {e}")
        return []
