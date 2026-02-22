"""
Advanced ML Recommendation Engine - Intermediate Level
Features:
- User-based Collaborative Filtering
- Hybrid Recommendations (Content + Collaborative + Popularity)
- User Preference Learning
- Cold Start Problem Handling
- Advanced Evaluation Metrics
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
from datetime import datetime, timedelta

class AdvancedRecommendationEngine:
    """
    Intermediate-level ML recommendation engine with:
    - Hybrid filtering (Content + Collaborative + Popularity)
    - User behavior tracking
    - Personalized recommendations
    - Cold start handling
    """
    
    def __init__(self, model_path="ml/advanced_model.pkl"):
        self.model_path = model_path
        self.user_item_matrix = None
        self.product_similarity = None
        self.user_similarity = None
        self.product_df = None
        self.user_df = None
        self.products_list = []
        self.users_list = []
        self.interaction_history = {}
        self.user_preferences = {}
        
    def train_from_database(self):
        """Train advanced model from Django database"""
        try:
            from app.models import Product, UserInteraction
            from django.db.models import Count, Avg
            
            print("\n🚀 Training Advanced Recommendation Engine...\n")
            
            # Load products
            products = list(Product.objects.all().values(
                'id', 'category', 'price', 'rating', 'total_reviews'
            ))
            
            if not products:
                print("❌ No products in database")
                return False
            
            self.product_df = pd.DataFrame(products)
            self.products_list = [p['id'] for p in products]
            
            # 1. BUILD PRODUCT SIMILARITY MATRIX
            print("1️⃣  Computing Product Similarity...")
            product_features = self._extract_product_features()
            self.product_similarity = cosine_similarity(product_features)
            print(f"   ✓ Product similarity matrix: {self.product_similarity.shape}")
            
            # 2. BUILD USER INTERACTION MATRIX
            print("2️⃣  Building User-Item Interaction Matrix...")
            interactions = list(UserInteraction.objects.all().values(
                'user_id', 'product_id', 'interaction_type', 'weight', 'rating_value'
            ))
            
            if interactions:
                interaction_df = pd.DataFrame(interactions)
                self.user_item_matrix = self._build_weighted_interaction_matrix(interaction_df)
                print(f"   ✓ User-item matrix: {self.user_item_matrix.shape}")
                
                # 3. BUILD USER SIMILARITY MATRIX
                print("3️⃣  Computing User Similarity...")
                if len(self.user_item_matrix) > 1:
                    self.user_similarity = cosine_similarity(self.user_item_matrix)
                    print(f"   ✓ User similarity matrix: {self.user_similarity.shape}")
                
                # 4. EXTRACT USER PREFERENCES
                print("4️⃣  Learning User Preferences...")
                self.user_preferences = self._extract_user_preferences(interaction_df)
                print(f"   ✓ Preferences learned for {len(self.user_preferences)} users")
            
            # 5. BUILD INTERACTION HISTORY FOR COLD START
            print("5️⃣  Building Interaction History...")
            self.interaction_history = self._build_interaction_history(interaction_df) if interactions else {}
            print(f"   ✓ History records: {len(self.interaction_history)}")
            
            self.save_model()
            print("\n✅ Advanced model trained successfully!\n")
            return True
            
        except Exception as e:
            print(f"❌ Training error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_product_features(self):
        """Extract and normalize product features"""
        try:
            # Normalize price
            prices = self.product_df['price'].values.reshape(-1, 1)
            scaler = StandardScaler()
            price_normalized = scaler.fit_transform(prices)
            
            # Category encoding (one-hot)
            categories = pd.get_dummies(self.product_df['category'], prefix='cat')
            
            # Rating impact
            ratings = self.product_df['rating'].values.reshape(-1, 1) / 5.0
            
            # Review count impact (normalized)
            reviews = self.product_df['total_reviews'].values.reshape(-1, 1)
            if reviews.max() > 0:
                reviews = reviews / reviews.max()
            else:
                reviews = np.zeros_like(reviews)
            
            # Combine all features
            features = np.hstack([
                price_normalized,
                categories.values,
                ratings,
                reviews
            ])
            
            return features
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return np.eye(len(self.product_df))
    
    def _build_weighted_interaction_matrix(self, interaction_df):
        """Build user-item matrix with weighted interactions"""
        try:
            # Aggregate interactions by weight
            interaction_pivot = interaction_df.groupby(['user_id', 'product_id'])['weight'].sum().reset_index()
            
            matrix = interaction_pivot.pivot_table(
                index='user_id',
                columns='product_id',
                values='weight'
            ).fillna(0)
            
            # Normalize by row (user)
            row_sums = matrix.sum(axis=1)
            row_sums[row_sums == 0] = 1  # Avoid division by zero
            matrix = matrix.div(row_sums, axis=0)
            
            self.users_list = list(matrix.index)
            return matrix
        except Exception as e:
            print(f"Matrix building error: {e}")
            return None
    
    def _extract_user_preferences(self, interaction_df):
        """Extract category and price preferences by user"""
        prefs = {}
        try:
            for user_id in interaction_df['user_id'].unique():
                user_interactions = interaction_df[interaction_df['user_id'] == user_id]
                
                # Get products they interacted with
                product_ids = user_interactions['product_id'].values
                products = self.product_df[self.product_df['id'].isin(product_ids)]
                
                if not products.empty:
                    prefs[user_id] = {
                        'preferred_categories': products['category'].mode().tolist(),
                        'avg_price': float(products['price'].mean()),
                        'interaction_count': len(user_interactions),
                        'avg_rating': float(products['rating'].mean())
                    }
        except Exception as e:
            print(f"Preference extraction error: {e}")
        
        return prefs
    
    def _build_interaction_history(self, interaction_df):
        """Build interaction history for cold start problem"""
        history = {}
        try:
            for user_id in interaction_df['user_id'].unique():
                user_interactions = interaction_df[interaction_df['user_id'] == user_id].sort_values('timestamp', ascending=False)
                history[user_id] = list(user_interactions['product_id'].values[:10])  # Last 10
        except Exception as e:
            print(f"History building error: {e}")
        
        return history
    
    def get_hybrid_recommendations(self, user_id=None, product_id=None, n_recommendations=6):
        """
        Get hybrid recommendations combining:
        1. Collaborative Filtering (if user has history)
        2. Content-Based (product similarity)
        3. Popularity (high rating + reviews)
        """
        try:
            if self.product_similarity is None:
                self.load_model()
            
            recommendations = {}
            
            # 1. COLLABORATIVE FILTERING SCORE
            if user_id and self.user_similarity is not None:
                collab_score = self._collaborative_score(user_id)
                recommendations['collaborative'] = collab_score
            
            # 2. CONTENT-BASED SCORE (from product)
            if product_id:
                content_score = self._content_based_score(product_id)
                recommendations['content_based'] = content_score
            
            # 3. POPULARITY SCORE
            popularity_score = self._popularity_score()
            recommendations['popularity'] = popularity_score
            
            # Combine scores (hybrid approach)
            final_scores = self._combine_scores(recommendations)
            
            # Get top recommendations
            if isinstance(final_scores, dict):
                sorted_products = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
                recommended_ids = [pid for pid, score in sorted_products[:n_recommendations]]
            else:
                recommended_ids = final_scores[:n_recommendations]
            
            return recommended_ids
        
        except Exception as e:
            print(f"Hybrid recommendation error: {e}")
            return self.get_trending_products(n_recommendations)
    
    def _collaborative_score(self, user_id):
        """Calculate collaborative filtering scores"""
        try:
            if user_id not in self.users_list:
                return {}
            
            user_idx = self.users_list.index(user_id)
            user_vector = self.user_item_matrix.iloc[user_idx].values
            
            # Find similar users
            similar_users_scores = self.user_similarity[user_idx]
            similar_user_indices = np.argsort(-similar_users_scores)[1:6]  # Top 5 similar
            
            # Aggregate products from similar users
            product_scores = {}
            for similar_idx in similar_user_indices:
                similar_user_vector = self.user_item_matrix.iloc[similar_idx].values
                
                # Products this user hasn't seen
                not_seen = user_vector == 0
                similar_products = similar_user_vector * not_seen
                
                for pid, score in enumerate(similar_products):
                    if score > 0:
                        product_scores[self.product_df.iloc[pid]['id']] = product_scores.get(
                            self.product_df.iloc[pid]['id'], 0
                        ) + score
            
            return product_scores
        except Exception as e:
            print(f"Collaborative score error: {e}")
            return {}
    
    def _content_based_score(self, product_id):
        """Calculate content-based filtering scores"""
        try:
            if product_id not in self.products_list:
                return {}
            
            product_idx = self.products_list.index(product_id)
            similarity_scores = self.product_similarity[product_idx]
            
            scores = {}
            for idx, score in enumerate(similarity_scores):
                if idx != product_idx:
                    scores[self.product_df.iloc[idx]['id']] = score
            
            return scores
        except Exception as e:
            print(f"Content-based score error: {e}")
            return {}
    
    def _popularity_score(self):
        """Calculate popularity scores (rating + review count)"""
        scores = {}
        try:
            for _, product in self.product_df.iterrows():
                # Normalize rating (0-5) and reviews
                rating_score = product['rating'] / 5.0
                review_score = min(product['total_reviews'] / 100.0, 1.0)  # Cap at 100 reviews
                
                # Weighted combination
                popularity = (rating_score * 0.6) + (review_score * 0.4)
                scores[product['id']] = popularity
        except Exception as e:
            print(f"Popularity score error: {e}")
        
        return scores
    
    def _combine_scores(self, recommendations):
        """Combine different recommendation scores using weighted average"""
        try:
            final_scores = {}
            all_product_ids = set()
            
            # Collect all products
            for score_dict in recommendations.values():
                all_product_ids.update(score_dict.keys())
            
            # Weighted average
            weights = {
                'collaborative': 0.4,
                'content_based': 0.35,
                'popularity': 0.25
            }
            
            for pid in all_product_ids:
                combined_score = 0
                total_weight = 0
                
                for category, weight in weights.items():
                    if category in recommendations:
                        score = recommendations[category].get(pid, 0)
                        combined_score += score * weight
                        if score > 0:
                            total_weight += weight
                
                if total_weight > 0:
                    final_scores[pid] = combined_score / total_weight
            
            return final_scores
        except Exception as e:
            print(f"Score combination error: {e}")
            return {}
    
    def get_trending_products(self, n_products=6):
        """Get trending products based on rating and reviews"""
        try:
            from app.models import Product
            trending = Product.objects.order_by('-rating', '-total_reviews')[:n_products]
            return list(trending.values_list('id', flat=True))
        except Exception as e:
            print(f"Trending error: {e}")
            return []
    
    def get_personalized_recommendations(self, user_id, n_recommendations=6):
        """Get personalized recommendations for a user"""
        try:
            if user_id in self.user_preferences:
                return self.get_hybrid_recommendations(user_id=user_id, n_recommendations=n_recommendations)
            else:
                # Cold start: recommend trending products
                return self.get_trending_products(n_recommendations)
        except Exception as e:
            print(f"Personalization error: {e}")
            return self.get_trending_products(n_recommendations)
    
    def save_model(self):
        """Save model to disk"""
        try:
            model_data = {
                'user_item_matrix': self.user_item_matrix,
                'product_similarity': self.product_similarity,
                'user_similarity': self.user_similarity,
                'product_df': self.product_df,
                'user_preferences': self.user_preferences,
                'interaction_history': self.interaction_history,
                'products_list': self.products_list,
                'users_list': self.users_list,
                'timestamp': datetime.now()
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✓ Model saved to {self.model_path}")
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load_model(self):
        """Load model from disk"""
        try:
            if not os.path.exists(self.model_path):
                print(f"⚠️  Model not found at {self.model_path}")
                return False
            
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.user_item_matrix = model_data.get('user_item_matrix')
            self.product_similarity = model_data.get('product_similarity')
            self.user_similarity = model_data.get('user_similarity')
            self.product_df = model_data.get('product_df')
            self.user_preferences = model_data.get('user_preferences', {})
            self.interaction_history = model_data.get('interaction_history', {})
            self.products_list = model_data.get('products_list', [])
            self.users_list = model_data.get('users_list', [])
            
            print(f"✓ Model loaded from {self.model_path}")
            return True
        except Exception as e:
            print(f"Load error: {e}")
            return False


# Global instance
advanced_recommendation_engine = AdvancedRecommendationEngine()
