import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import pickle
import os

class ModelEvaluator:
    """Evaluate the recommendation model performance"""
    
    @staticmethod
    def load_model(model_path="ml/model.pkl"):
        """Load trained model"""
        try:
            with open(model_path, "rb") as f:
                data = pickle.load(f)
            return data
        except:
            return None
    
    @staticmethod
    def evaluate_collaborative_filtering(user_item_matrix):
        """Evaluate collaborative filtering model"""
        try:
            if user_item_matrix is None or user_item_matrix.empty:
                return {"error": "No data to evaluate"}
            
            # Simple evaluation: check coverage and sparsity
            total_interactions = (user_item_matrix != 0).sum().sum()
            possible_interactions = user_item_matrix.shape[0] * user_item_matrix.shape[1]
            sparsity = 1 - (total_interactions / possible_interactions)
            
            return {
                "users": user_item_matrix.shape[0],
                "products": user_item_matrix.shape[1],
                "total_interactions": int(total_interactions),
                "sparsity": float(sparsity),
                "coverage": float(1 - sparsity)
            }
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def print_evaluation():
        """Print model evaluation report"""
        data = ModelEvaluator.load_model()
        
        if not data or data.get('user_item_matrix') is None:
            print("❌ No model found to evaluate")
            return
        
        print("\n" + "="*50)
        print("   RECOMMENDATION MODEL EVALUATION REPORT")
        print("="*50 + "\n")
        
        stats = ModelEvaluator.evaluate_collaborative_filtering(data.get('user_item_matrix'))
        
        for key, value in stats.items():
            if key != "error":
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "="*50)


if __name__ == "__main__":
    ModelEvaluator.print_evaluation()
