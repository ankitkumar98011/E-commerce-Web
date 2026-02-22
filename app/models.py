
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('product_approved', 'Product Approved'),
        ('product_rejected', 'Product Rejected'),
        ('product_sold', 'Product Sold'),
        ('product_returned', 'Product Returned'),
        ('custom', 'Custom'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPE_CHOICES, default='custom')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')

    def __str__(self):
        return f"{self.user.username}: {self.notif_type} - {self.message[:30]}..."

import django.core.validators
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default-avatar.png')
    bio = models.TextField(max_length=500, blank=True)
    
    # Location fields
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10, blank=True, default='')
    address = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"


class SellerProfile(models.Model):
    """Seller account profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    seller_id = models.CharField(max_length=20, unique=True, editable=False)  # Format: SEL-XXXXX
    shop_name = models.CharField(max_length=255)
    shop_description = models.TextField(blank=True)
    shop_image = models.ImageField(upload_to='shops/', null=True, blank=True)
    
    # Stats
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0,
                                validators=[django.core.validators.MinValueValidator(0),
                                           django.core.validators.MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)
    total_products = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Bank Details for Payments
    account_holder_name = models.CharField(max_length=255, blank=True, default='')
    bank_name = models.CharField(max_length=255, blank=True, default='')
    account_number = models.CharField(max_length=20, blank=True, default='')
    ifsc_code = models.CharField(max_length=20, blank=True, default='')
    branch_name = models.CharField(max_length=255, blank=True, default='')
    bank_verified = models.BooleanField(default=False, help_text="Bank details verified by admin")
    
    # Verification
    is_verified = models.BooleanField(default=False, help_text="Admin verification status")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.shop_name} ({self.seller_id})"
    
    def save(self, *args, **kwargs):
        """Generate seller_id if not exists"""
        if not self.seller_id:
            # Generate unique seller ID: SEL-XXXXX
            random_suffix = str(uuid.uuid4())[:5].upper()
            self.seller_id = f"SEL-{random_suffix}"
        super().save(*args, **kwargs)

class Product(models.Model):
    QUALITY_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Discounted price (if any)")
    is_discounted = models.BooleanField(default=False, help_text="Is product currently discounted?")
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='standard')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0, 
                                  validators=[django.core.validators.MinValueValidator(0), 
                                             django.core.validators.MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    
    # Seller information
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_products', null=True, blank=True)
    is_user_uploaded = models.BooleanField(default=False, help_text="Whether product was uploaded by user")
    product_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    # Warranty fields (sellers can add warranty information for eligible products)
    warranty_provided = models.BooleanField(default=False, help_text="Whether seller provides warranty for this product")
    warranty_days = models.PositiveIntegerField(default=0, help_text="Number of warranty days offered by seller")
    warranty_terms = models.TextField(blank=True, default='', help_text="Optional warranty terms/notes provided by seller")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class UserInteraction(models.Model):
    """
    Track user interactions with products for ML recommendations
    Supports: views, clicks, purchases, ratings, cart additions
    """
    INTERACTION_TYPES = [
        ('view', 'Product View'),
        ('click', 'Product Click'),
        ('purchase', 'Purchase'),
        ('rating', 'Product Rating'),
        ('cart', 'Add to Cart'),
        ('wishlist', 'Add to Wishlist'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    rating_value = models.PositiveIntegerField(null=True, blank=True, 
                                              help_text="Rating given by user (1-5)")
    weight = models.FloatField(default=1.0, help_text="Weight for ML algorithm")
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, help_text="Session identifier")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['product', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        """Auto-assign weights based on interaction type"""
        interaction_weights = {
            'view': 1.0,
            'click': 2.0,
            'cart': 3.0,
            'wishlist': 2.5,
            'purchase': 5.0,
            'rating': 4.0,
        }
        if not self.weight:
            self.weight = interaction_weights.get(self.interaction_type, 1.0)
        super().save(*args, **kwargs)


class Cart(models.Model):
    """Shopping cart for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart - {self.user.username}"
    
    def get_total(self):
        """Calculate cart total"""
        return sum(item.get_subtotal() for item in self.items.all())
    
    def get_item_count(self):
        """Get total items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Items in a shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def get_subtotal(self):
        """Calculate price for this item"""
        return float(self.product.price) * self.quantity


class Order(models.Model):
    """Purchase orders"""
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Payment method choices
    PAYMENT_METHODS = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Debit/Credit Card'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Shipping details
    full_name = models.CharField(max_length=100, default='')
    shipping_address = models.TextField()
    city = models.CharField(max_length=50, default='')
    pincode = models.CharField(max_length=6, default='')
    phone_number = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class OrderTracking(models.Model):
    """Tracks order status changes with time and location"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_updates')
    status = models.CharField(max_length=20)
    location = models.CharField(max_length=255, blank=True, default='')
    details = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.order.order_number} - {self.status} at {self.location} ({self.timestamp:%Y-%m-%d %H:%M})"


class ChatMessage(models.Model):
    """AI-based chat messages for customer support"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_messages')
    message = models.TextField()
    is_user = models.BooleanField(default=True)  # True if user message, False if AI response
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."


class ReturnRequest(models.Model):
    """Customer return/exchange requests"""
    REQUEST_TYPES = [
        ('return', 'Return'),
        ('exchange', 'Exchange'),
    ]
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='return_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    reason = models.TextField()
    customer_account_name = models.CharField(max_length=255, blank=True, default='')
    customer_account_number = models.CharField(max_length=50, blank=True, default='')
    customer_ifsc = models.CharField(max_length=20, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReturnRequest #{self.id} for {self.order.order_number} ({self.request_type})"