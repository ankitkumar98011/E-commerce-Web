import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

class RecommendationEngine:
    """
    ML-powered recommendation engine for e-commerce
    Uses collaborative filtering and content-based recommendations
    """
    
    def __init__(self, model_path="ml/model.pkl"):
        self.model_path = model_path
        self.user_item_matrix = None
        self.product_similarity = None
        self.product_df = None
        self.products_list = []
        
    def train_from_data(self, csv_path="data/transactions.csv"):
        """Train model from transactions CSV"""
        try:
            df = pd.read_csv(csv_path)
            
            # Create user-item matrix
            self.user_item_matrix = df.pivot_table(
                index="user_id",
                columns="product_id",
                values="rating"
            ).fillna(0)
            
            # Calculate user-based collaborative filtering similarity
            user_similarity = cosine_similarity(self.user_item_matrix)
            
            # Calculate product similarity
            product_similarity = cosine_similarity(self.user_item_matrix.T)
            
            self.product_similarity = product_similarity
            
            self.save_model()
            print("✓ Model trained from CSV successfully")
            return True
        except Exception as e:
            print(f"Error training from CSV: {e}")
            return False
    
    def train_from_database(self):
        """Train model from Django database directly"""
        try:
            # Import here to avoid circular imports
            from app.models import Product
            
            products = list(Product.objects.all().values())
            
            if not products:
                print("No products in database")
                return False
            
            self.product_df = pd.DataFrame(products)
            self.products_list = [p['id'] for p in products]
            
            # Content-based: Category + Price similarity
            if len(self.products_list) > 1:
                # Create simple feature vectors
                categories = self.product_df['category'].str.lower()
                prices = self.product_df['price'].values.reshape(-1, 1)
                
                # Normalize prices
                price_normalized = (prices - prices.min()) / (prices.max() - prices.min() + 1)
                
                # Combine features
                features = []
                for idx, row in self.product_df.iterrows():
                    cat_vec = [1 if row['category'].lower() == cat else 0 for cat in categories.unique()]
                    price_feat = price_normalized[idx].tolist()
                    features.append(cat_vec + price_feat)
                
                features_array = np.array(features)
                self.product_similarity = cosine_similarity(features_array)
            
            self.save_model()
            print("✓ Model trained from database successfully")
            return True
        except Exception as e:
            print(f"Error training from database: {e}")
            return False
    
    def get_recommendations(self, product_id, n_recommendations=5):
        """Get product recommendations based on similarity"""
        try:
            if self.product_similarity is None:
                self.load_model()
            
            if self.product_df is None:
                from app.models import Product
                self.product_df = pd.DataFrame(list(Product.objects.all().values()))
            
            # Find product index
            if product_id not in self.product_df['id'].values:
                return []
            
            product_idx = self.product_df[self.product_df['id'] == product_id].index[0]
            
            # Get similarity scores
            sim_scores = list(enumerate(self.product_similarity[product_idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top recommendations (excluding the product itself)
            sim_scores = sim_scores[1:n_recommendations+1]
            product_indices = [i[0] for i in sim_scores]
            
            recommended_ids = self.product_df.iloc[product_indices]['id'].tolist()
            return recommended_ids
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def get_trending_products(self, n_products=6):
        """Get trending/popular products"""
        try:
            from app.models import Product
            # For now, return recently created products
            # This can be enhanced with view counts or ratings
            trending = Product.objects.all().order_by('-created_at')[:n_products]
            return list(trending.values_list('id', flat=True))
        except Exception as e:
            print(f"Error getting trending products: {e}")
            return []
    
    def get_recommended_for_user(self, user_id=None, n_recommendations=6):
        """Get personalized recommendations for a user"""
        try:
            from app.models import Product
            
            if not user_id:
                # Return trending if no user specified
                return self.get_trending_products(n_recommendations)
            
            # For un-rated users, return trending products
            if self.user_item_matrix is None:
                return self.get_trending_products(n_recommendations)
            
            if user_id not in self.user_item_matrix.index:
                return self.get_trending_products(n_recommendations)
            
            user_idx = self.user_item_matrix.index.get_loc(user_id)
            user_ratings = self.user_item_matrix.iloc[user_idx]
            
            # Get user's highly rated products
            highly_rated = user_ratings[user_ratings > 3].index.tolist()
            
            recommendations = set()
            for product_id in highly_rated:
                rec = self.get_recommendations(product_id, 2)
                recommendations.update(rec)
            
            # Also add trending products
            trending = self.get_trending_products(n_recommendations)
            recommendations.update(trending)
            
            recommendations = list(recommendations)[:n_recommendations]
            return recommendations
        except Exception as e:
            print(f"Error getting user recommendations: {e}")
            return []
    
    def save_model(self):
        """Save trained model to pickle file"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump({
                    'user_item_matrix': self.user_item_matrix,
                    'product_similarity': self.product_similarity,
                    'product_df': self.product_df,
                    'products_list': self.products_list
                }, f)
            print(f"✓ Model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load trained model from pickle file"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                    self.user_item_matrix = data.get('user_item_matrix')
                    self.product_similarity = data.get('product_similarity')
                    self.product_df = data.get('product_df')
                    self.products_list = data.get('products_list', [])
                print("✓ Model loaded successfully")
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        return False


# Global instance
recommendation_engine = RecommendationEngine()
