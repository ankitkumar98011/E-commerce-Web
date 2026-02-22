# 🤖 ML Recommendation Engine - SmartShop

## Overview
The ML engine provides intelligent product recommendations using:
- **Collaborative Filtering**: User-product interactions
- **Content-Based Filtering**: Product similarity (category, price)
- **Trending Analysis**: Popular products based on activity

## Training Model

### Method 1: Django Management Command (Recommended)
```bash
# Train from database (uses products in DB)
python manage.py train_ml_model --source database

# Train from CSV files
python manage.py train_ml_model --source csv
```

### Method 2: Python Script
```bash
# Auto-train script (periodic training)
python ml/train_model.py database

# Or from CSV
python ml/train_model.py csv
```

### Method 3: Auto-Training Scheduler
```bash
# Run background scheduler (trains every 6 hours)
pip install schedule
python ml/auto_train.py
```

## Auto-Training Features

### 1. **Signal-Based Auto-Training**
When a new product is added to the database, the model automatically retrains in the background.

```python
# In app/signals.py
# Triggered automatically on Product creation
```

### 2. **Scheduled Auto-Training**
Run periodic training with the scheduler:

```bash
python ml/auto_train.py
```

**Schedule:**
- Training: Every 6 hours
- Evaluation: Every 12 hours

## Using Recommendations

### In Views
```python
from ml.recommendation import recommendation_engine

# Get product recommendations
recommended_ids = recommendation_engine.get_recommendations(product_id=5, n_recommendations=6)
recommended_products = Product.objects.filter(id__in=recommended_ids)

# Get trending products
trending_ids = recommendation_engine.get_trending_products(n_products=6)

# Get personalized recommendations for user
user_recs = recommendation_engine.get_recommended_for_user(user_id=1)
```

### In Templates
```django
{% for product in recommended_products %}
    <div class="product-card">
        <h3>{{ product.name }}</h3>
        <p>${{ product.price }}</p>
    </div>
{% endfor %}
```

## Model Evaluation

### View Model Performance
```bash
# Run evaluation
python -c "from ml.evaluate import ModelEvaluator; ModelEvaluator.print_evaluation()"
```

### Metrics Tracked
- **Users Covered**: Number of unique users in training data
- **Products**: Number of unique products
- **Total Interactions**: User-product interactions count
- **Sparsity**: Data sparsity (how sparse the interaction matrix is)
- **Coverage**: How well the model covers products

## File Structure

```
ml/
├── train_model.py          # Main training script
├── recommendation.py        # Recommendation engine (core)
├── evaluate.py             # Model evaluation tools
├── auto_train.py           # Auto-training scheduler
└── model.pkl               # Trained model (auto-generated)

app/
├── signals.py              # Auto-training on product creation
├── management/
│   └── commands/
│       └── train_ml_model.py  # Django management command
```

## Configuration

### Model Path
Default: `ml/model.pkl`

Change in code:
```python
from ml.recommendation import RecommendationEngine
engine = RecommendationEngine(model_path="custom/path/model.pkl")
```

### Training Data Source
- **Database**: Uses Product model from Django ORM
- **CSV**: Uses `data/transactions.csv`

## Troubleshooting

### Model Not Found
```python
# Auto-load or train if missing
recommendation_engine.load_model()
if recommendation_engine.product_similarity is None:
    recommendation_engine.train_from_database()
```

### Slow Training
- Reduce product count in your test data
- Use CSV for smaller datasets
- Run training during off-peak hours

### No Recommendations
1. Check if model is trained: `ls ml/model.pkl`
2. Train manually: `python manage.py train_ml_model`
3. Verify products in database: `python manage.py shell`

```python
from app.models import Product
print(Product.objects.count())
```

## Performance Tips

1. **Cache Recommendations**
   ```python
   from django.views.decorators.cache import cache_page
   
   @cache_page(60 * 60)  # Cache for 1 hour
   def get_recommendations(request):
       ...
   ```

2. **Async Training**
   - Use Celery for background tasks
   - Schedule training at night

3. **Model Size**
   - Keep model pickle file optimized
   - Retrain periodically to remove old data

## Integration Points

### Automatically Integrated:
- ✅ Home page recommendations
- ✅ Product detail page (similar products)
- ✅ Product list page (trending)

### Can Be Extended To:
- Search results ranking
- Email recommendations
- API endpoints
- Admin dashboard

## Next Steps

1. **Train Initial Model**
   ```bash
   python manage.py train_ml_model
   ```

2. **Add Sample Products** (if needed)
   ```bash
   python manage.py shell
   ```

3. **View Recommendations**
   Visit homepage to see recommended products

4. **Monitor Training** (Optional)
   ```bash
   python ml/auto_train.py
   ```

---

🎯 **The model will automatically update** when new products are added!
