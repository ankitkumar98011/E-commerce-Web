from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from .models import Product, UserProfile, UserInteraction, Cart, CartItem, Order, OrderItem, SellerProfile, ReturnRequest
from ml.recommendation import recommendation_engine
from ml.advanced_recommendation import advanced_recommendation_engine
from .forms import ProductUploadForm, CheckoutForm, AddToCartForm, ProductEditForm


@login_required(login_url='app:login')
def edit_product(request, product_id):
    """Allow sellers to edit their own products"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        form = ProductEditForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('app:my_products')
        else:
            messages.error(request, 'Please fix the errors below')
    else:
        form = ProductEditForm(instance=product)
    return render(request, 'upload_product.html', {'form': form, 'edit_mode': True, 'product': product})


@login_required(login_url='app:login')
def delete_product(request, product_id):
    """Allow sellers to delete their own products"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('app:my_products')
    return render(request, 'confirm_delete.html', {'product': product})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from .models import Product, UserProfile, UserInteraction, Cart, CartItem, Order, OrderItem, SellerProfile, ReturnRequest
from ml.recommendation import recommendation_engine
from ml.advanced_recommendation import advanced_recommendation_engine
from .forms import ProductUploadForm, CheckoutForm, AddToCartForm
from .tracking import track_user_interaction, get_user_session_id, get_similar_products
import uuid

def home(request):
    products = Product.objects.all().order_by('-created_at')
    
    # Load advanced ML model
    if advanced_recommendation_engine.product_similarity is None:
        advanced_recommendation_engine.load_model()
    
    # Get personalized recommendations if user is logged in
    if request.user.is_authenticated:
        recommended_ids = advanced_recommendation_engine.get_personalized_recommendations(
            user_id=request.user.id, n_recommendations=6
        )
    else:
        # Get trending for anonymous users
        recommended_ids = advanced_recommendation_engine.get_trending_products(6)
    
    recommended_products = Product.objects.filter(id__in=recommended_ids) if recommended_ids else []
    
    # Get trending products
    trending_ids = advanced_recommendation_engine.get_trending_products(6)
    trending_products = Product.objects.filter(id__in=trending_ids) if trending_ids else []
    
    context = {
        'products': products[:6],
        'recommended_products': recommended_products,
        'trending_products': trending_products
    }
    return render(request, 'home.html', context)


def search_suggestions(request):
    """API endpoint for search suggestions/autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Search products by name, category, and description
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(category__icontains=query)
    ).distinct()[:10]
    
    suggestions = [
        {
            'id': product.id,
            'name': product.name,
            'category': product.category,
            'price': str(product.price),
            'rating': product.rating,
            'image': product.image.url if product.image else '/static/images/no-image.png'
        }
        for product in products
    ]
    
    return JsonResponse({'suggestions': suggestions})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Track product view
    session_id = get_user_session_id(request)
    if request.user.is_authenticated:
        track_user_interaction(request.user, product, 'view', session_id=session_id)
    
    # Get similar products
    similar_products = get_similar_products(product.id, n=5)
    
    # Get hybrid recommendations for this product
    if advanced_recommendation_engine.product_similarity is None:
        advanced_recommendation_engine.load_model()
    
    if request.user.is_authenticated:
        # Personalized recommendations
        recommended_ids = advanced_recommendation_engine.get_hybrid_recommendations(
            user_id=request.user.id,
            product_id=pk,
            n_recommendations=6
        )
    else:
        # Content-based recommendations
        recommended_ids = advanced_recommendation_engine.get_hybrid_recommendations(
            product_id=pk,
            n_recommendations=6
        )
    
    recommended_products = Product.objects.filter(id__in=recommended_ids) if recommended_ids else []
    
    context = {
        'product': product,
        'similar_products': similar_products,
        'recommended_products': recommended_products
    }
    return render(request, 'product.html', context)

def products_list(request):
    products = Product.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category__icontains=category)
    
    # Price filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            min_price = None
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            max_price = None
    
    # Rating filter
    min_rating = request.GET.get('min_rating')
    if min_rating:
        try:
            products = products.filter(rating__gte=float(min_rating))
        except (ValueError, TypeError):
            min_rating = None
    
    # Get unique categories for filter dropdown
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    # Get price range for filter
    all_products = Product.objects.all()
    prices = [p.price for p in all_products]
    min_product_price = min(prices) if prices else 0
    max_product_price = max(prices) if prices else 0
    
    context = {
        'products': products,
        'search_query': search_query,
        'categories': categories,
        'selected_category': category,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'min_rating': min_rating or '',
        'min_product_price': int(min_product_price),
        'max_product_price': int(max_product_price),
        'display_min_price': min_price or int(min_product_price),
        'display_max_price': max_price or int(max_product_price),
    }
    return render(request, 'products.html', context) 

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            return render(request, 'login.html', {'error': 'Please fill in all fields'})
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('app:home')
            else:
                return render(request, 'login.html', {'error': 'Invalid password'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'Email not found. Please sign up.'})
    
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validation
        if not all([first_name, email, password, password2]):
            return render(request, 'signup.html', {'error': 'Please fill in all fields'})
        
        if password != password2:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
        
        if len(password) < 6:
            return render(request, 'signup.html', {'error': 'Password must be at least 6 characters'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})
        
        if User.objects.filter(username=email).exists():
            return render(request, 'signup.html', {'error': 'Username already taken'})
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name
            )
            # Create UserProfile for the new user
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome {first_name}! Your account has been created.')
            return redirect('app:home')
        except Exception as e:
            return render(request, 'signup.html', {'error': f'Error creating account: {str(e)}'})
    
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('app:home')

@login_required(login_url='app:login')
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            first_name = request.POST.get('first_name')
            email = request.POST.get('email')
            bio = request.POST.get('bio')
            
            if not first_name or not email:
                messages.error(request, 'Please fill in all fields')
            elif User.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, 'Email already in use')
            else:
                user.first_name = first_name
                user.email = email
                user.save()
                profile.bio = bio
                profile.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('app:profile')
        
        elif action == 'upload_avatar':
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
                profile.save()
                messages.success(request, 'Profile photo updated successfully!')
                return redirect('app:profile')
            else:
                messages.error(request, 'Please select an image')
        
        elif action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not user.check_password(old_password):
                messages.error(request, 'Old password is incorrect')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            elif len(new_password) < 6:
                messages.error(request, 'Password must be at least 6 characters')
            else:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully!')
                return redirect('app:profile')
    
    return render(request, 'profile.html', {'user': user, 'profile': profile})


# ===== ADVANCED ML API ENDPOINTS =====

def get_personalized_recommendations(request):
    """API endpoint for getting personalized recommendations"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'User must be logged in'
            })
        
        n_recommendations = int(request.GET.get('n', 6))
        
        # Load model
        if advanced_recommendation_engine.product_similarity is None:
            advanced_recommendation_engine.load_model()
        
        # Get recommendations
        recommended_ids = advanced_recommendation_engine.get_personalized_recommendations(
            user_id=request.user.id,
            n_recommendations=n_recommendations
        )
        
        products = Product.objects.filter(id__in=recommended_ids).values(
            'id', 'name', 'price', 'rating', 'category', 'image'
        )
        
        return JsonResponse({
            'success': True,
            'recommendations': list(products)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def track_interaction(request):
    """API endpoint for tracking user interactions"""
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'User must be logged in'
            })
        
        product_id = int(request.POST.get('product_id'))
        interaction_type = request.POST.get('interaction_type', 'view')
        rating_value = request.POST.get('rating_value')
        
        product = Product.objects.get(id=product_id)
        session_id = get_user_session_id(request)
        
        # Track interaction
        interaction = track_user_interaction(
            user=request.user,
            product=product,
            interaction_type=interaction_type,
            rating_value=int(rating_value) if rating_value else None,
            session_id=session_id
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{interaction_type} tracked',
            'interaction_id': interaction.id if interaction else None
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def get_hybrid_recommendations(request):
    """API endpoint for hybrid recommendations"""
    try:
        product_id = int(request.GET.get('product_id', 0))
        n = int(request.GET.get('n', 6))
        
        if advanced_recommendation_engine.product_similarity is None:
            advanced_recommendation_engine.load_model()
        
        # Get hybrid recommendations
        if request.user.is_authenticated:
            recommended_ids = advanced_recommendation_engine.get_hybrid_recommendations(
                user_id=request.user.id,
                product_id=product_id if product_id else None,
                n_recommendations=n
            )
        else:
            recommended_ids = advanced_recommendation_engine.get_hybrid_recommendations(
                product_id=product_id if product_id else None,
                n_recommendations=n
            )
        
        products = Product.objects.filter(id__in=recommended_ids).values(
            'id', 'name', 'price', 'rating', 'category'
        )
        
        return JsonResponse({
            'success': True,
            'recommendations': list(products)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# ===== E-COMMERCE: PRODUCT UPLOAD =====

@login_required(login_url='app:login')
def upload_product(request):
    """Allow users to upload and sell products"""
    if request.method == 'POST':
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.is_user_uploaded = True
            product.product_status = 'pending'  # Needs review
            product.save()
            
            messages.success(request, '✅ Product uploaded successfully! Awaiting admin approval.')
            return redirect('app:my_products')
        else:
            messages.error(request, '❌ Please fix the errors below')
    else:
        form = ProductUploadForm()
    
    return render(request, 'upload_product.html', {'form': form})


@login_required(login_url='app:login')
def my_products(request):
    """View user's uploaded products"""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    context = {
        'products': products,
        'total_products': products.count(),
        'approved_products': products.filter(product_status='approved').count(),
        'pending_products': products.filter(product_status='pending').count(),
    }
    return render(request, 'my_products.html', context)


# ===== E-COMMERCE: SHOPPING CART =====

def add_to_cart(request, product_id):
    """Add product to shopping cart"""
    # Check if user is authenticated first
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Please log in to add items to cart',
            'redirect': '/login/?next=' + request.path
        }, status=401)
    
    if request.method not in ['POST', 'PUT']:
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=400)
    
    try:
        product = get_object_or_404(Product, id=product_id, product_status='approved')
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Handle both JSON and POST data
        try:
            import json
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({'success': False, 'message': 'Invalid quantity'})
        
        if quantity > product.stock:
            return JsonResponse({'success': False, 'message': f'Only {product.stock} items available'})
        
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not item_created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        
        # Track interaction
        track_user_interaction(request.user, product, 'cart')
        
        return JsonResponse({
            'success': True,
            'message': f'✅ {product.name} added to cart',
            'cart_count': cart.items.count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='app:login')
def view_cart(request):
    """View shopping cart"""
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'total': cart.get_total(),
        'item_count': cart.get_item_count()
    }
    return render(request, 'cart.html', context)


def remove_from_cart(request, item_id):
    """Remove item from cart"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Please log in to manage your cart',
            'redirect': '/login/'
        }, status=401)
    
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{product_name} removed from cart'
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


def update_cart_item(request, item_id):
    """Update quantity of cart item"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Please log in to manage your cart',
            'redirect': '/login/'
        }, status=401)
    
    try:
        # Handle both JSON and POST data
        try:
            import json
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            quantity = int(request.POST.get('quantity', 1))
        
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Only {cart_item.product.stock} items available'
                })
            
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total(),
            'item_count': cart.items.count()
        })
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


# ===== E-COMMERCE: CHECKOUT & ORDERS =====

@login_required(login_url='app:login')
def checkout(request):
    """Checkout page"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to checkout')
        return redirect('app:login')
    
    try:
        cart = Cart.objects.get(user=request.user)
        if cart.items.count() == 0:
            messages.warning(request, 'Your cart is empty!')
            return redirect('app:products')
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty!')
        return redirect('app:products')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order from form
            order = form.save(commit=False)
            order.user = request.user
            order.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
            order.total_amount = cart.get_total()
            payment_method = form.cleaned_data.get('payment_method')
            
            # For CoD, set as confirmed. For others, keep pending until payment
            if payment_method == 'cod':
                order.payment_status = 'completed'
                order.order_status = 'confirmed'
            else:
                order.payment_status = 'pending'
                order.order_status = 'pending'
            
            order.save()
            
            # Move cart items to order
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                    subtotal=cart_item.get_subtotal()
                )
                
                # Track purchase interaction
                track_user_interaction(
                    request.user,
                    cart_item.product,
                    'purchase',
                    session_id=get_user_session_id(request)
                )
            
            # Clear cart
            cart.items.all().delete()
            
            # If CoD, go directly to confirmation
            if payment_method == 'cod':
                messages.success(request, f'✅ Order placed! You will pay ₹{order.total_amount} on delivery. Order #: {order.order_number}')
                return redirect('app:order_confirmation', order_id=order.id)
            else:
                # For card/UPI, redirect to payment gateway
                return redirect('app:process_payment', order_id=order.id)
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field}: {", ".join(errors)}')
    else:
        form = CheckoutForm()
    
    context = {
        'cart': cart,
        'form': form,
        'total': cart.get_total()
    }
    return render(request, 'checkout.html', context)


@login_required(login_url='app:login')
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all()
    }
    return render(request, 'order_confirmation.html', context)


@login_required(login_url='app:login')
def my_orders(request):
    """View user's orders"""
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders,
        'total_orders': orders.count(),
        'total_spent': sum(order.total_amount for order in orders)
    }
    return render(request, 'my_orders.html', context)


@login_required(login_url='app:login')
def order_detail(request, order_id):
    """Show full order details, payment info, tracking, invoice and actions"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('product').all()

    # Determine if invoice is available: any electronics item with seller warranty
    invoice_available = any(
        (item.product.category.lower() == 'electronics' and getattr(item.product, 'warranty_provided', False))
        for item in order_items
    )

    tracking_updates = order.tracking_updates.all()
    context = {
        'order': order,
        'order_items': order_items,
        'invoice_available': invoice_available,
        'return_requests': order.return_requests.all(),
        'tracking_updates': tracking_updates
    }
    return render(request, 'order_detail.html', context)


@login_required(login_url='app:login')
def cancel_order(request, order_id):
    """Allow user to cancel order if it hasn't shipped/delivered"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.order_status in ['shipped', 'delivered']:
        messages.error(request, 'Order cannot be cancelled after it is shipped or delivered')
        return redirect('app:order_detail', order_id=order.id)

    order.order_status = 'cancelled'
    order.payment_status = 'failed' if order.payment_status != 'completed' else order.payment_status
    order.save()
    messages.success(request, 'Order cancelled successfully')
    return redirect('app:my_orders')


@login_required(login_url='app:login')
def request_return(request, order_id):
    """Handle return/exchange requests within 7 days after delivery"""
    from django.utils import timezone
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Only allow return/exchange if order is delivered and within 7 days
    if order.order_status != 'delivered':
        messages.error(request, 'Return/Exchange allowed only after delivery')
        return redirect('app:order_detail', order_id=order.id)

    delivered_at = order.updated_at
    if (timezone.now() - delivered_at).days > 7:
        messages.error(request, 'Return/Exchange period (7 days) has expired')
        return redirect('app:order_detail', order_id=order.id)

    if request.method == 'POST':
        req_type = request.POST.get('request_type')
        reason = request.POST.get('reason')
        acct_name = request.POST.get('account_name')
        acct_number = request.POST.get('account_number')
        ifsc = request.POST.get('ifsc')

        if not all([req_type, reason]):
            messages.error(request, 'Please provide request type and reason')
            return redirect('app:order_detail', order_id=order.id)

        rr = ReturnRequest.objects.create(
            order=order,
            request_type=req_type,
            reason=reason,
            customer_account_name=acct_name or '',
            customer_account_number=acct_number or '',
            customer_ifsc=ifsc or ''
        )

        messages.success(request, 'Your return/exchange request has been submitted')
        return redirect('app:order_detail', order_id=order.id)

    # GET: show return form
    return render(request, 'return_form.html', {'order': order})


@login_required(login_url='app:login')
def invoice_view(request, order_id):
    """Render invoice for eligible orders (electronics with warranty)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.select_related('product').all()

    eligible = [item for item in order_items if item.product.category.lower() == 'electronics' and getattr(item.product, 'warranty_provided', False)]
    if not eligible:
        messages.error(request, 'Invoice not available for this order')
        return redirect('app:order_detail', order_id=order.id)

    context = {
        'order': order,
        'order_items': order_items,
        'eligible_items': eligible
    }
    return render(request, 'invoice.html', context)


# ===== PAYMENT PROCESSING =====

@login_required(login_url='app:login')
def process_payment(request, order_id):
    """Process payment for online payment methods (Card/UPI)"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # If order is already paid, go to confirmation
    if order.payment_status == 'completed':
        return redirect('app:order_confirmation', order_id=order.id)
    
    # Only allow payment for pending orders
    if order.payment_status != 'pending':
        messages.error(request, 'This order cannot be paid for at this time')
        return redirect('app:my_orders')
    
    context = {
        'order': order,
        'order_items': order.items.all(),
        'payment_method': order.payment_method.upper() if order.payment_method == 'upi' else 'Card',
        'razorpay_key': 'rzp_test_XXXXXXXXXXXX',  # Would be from settings in production
    }
    return render(request, 'payment.html', context)


@login_required(login_url='app:login')
def verify_payment(request, order_id):
    """Verify and complete payment"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    try:
        # In a real scenario, you would verify the payment with Razorpay/Stripe
        # For now, we'll simulate successful payment
        
        payment_method = order.payment_method.upper()
        
        # Update order payment status
        order.payment_status = 'completed'
        order.order_status = 'confirmed'
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'✅ Payment successful via {payment_method}!',
            'order_id': order.id,
            'order_number': order.order_number
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Payment verification failed: {str(e)}'
        }, status=400)


@csrf_exempt
def payment_callback(request):
    """
    Webhook endpoint for payment gateway callbacks (Razorpay, Stripe, etc.)
    This would be called by the payment gateway after payment is processed.
    
    For Razorpay: Payment details are sent via POST
    For Stripe: Webhook signature verification is required
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid'}, status=400)
    
    try:
        import json
        data = json.loads(request.body)
        
        # Get the order ID from the payment response
        order_id = data.get('order_id')
        payment_id = data.get('payment_id')
        payment_status = data.get('status')  # success, failed, pending
        
        order = Order.objects.get(id=order_id)
        
        if payment_status == 'success':
            order.payment_status = 'completed'
            order.order_status = 'confirmed'
            order.save()
            
            # You could send an email confirmation here
            return JsonResponse({'status': 'success', 'message': 'Payment verified'})
        else:
            order.payment_status = 'failed'
            order.order_status = 'cancelled'
            order.save()
            
            return JsonResponse({'status': 'failed', 'message': 'Payment failed'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ===== SELLER SYSTEM =====

@login_required(login_url='app:login')
def become_seller(request):
    """Register as a seller"""
    # Check if user is already a seller
    try:
        seller = request.user.seller_profile
        messages.info(request, f'✅ You are already a seller! Your Seller ID: {seller.seller_id}')
        return redirect('app:seller_dashboard')
    except SellerProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name', '')
        shop_description = request.POST.get('shop_description', '')
        
        if not shop_name:
            messages.error(request, '❌ Shop name is required')
            return render(request, 'become_seller.html')
        
        # Create seller profile
        seller = SellerProfile.objects.create(
            user=request.user,
            shop_name=shop_name,
            shop_description=shop_description
        )
        
        messages.success(request, f'🎉 Congratulations! You are now a seller!\n\nYour Seller ID: {seller.seller_id}\n\nYou can now start uploading products!')
        return redirect('app:seller_dashboard')
    
    context = {}
    return render(request, 'become_seller.html', context)


@login_required(login_url='app:login')
def seller_dashboard(request):
    """Seller dashboard - view products and stats"""
    try:
        seller = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.error(request, '❌ You are not registered as a seller. Please register first.')
        return redirect('app:become_seller')
    
    # Get all products uploaded by this seller
    products = Product.objects.filter(seller=request.user, is_user_uploaded=True)
    
    # Calculate stats
    approved_products = products.filter(product_status='approved').count()
    pending_products = products.filter(product_status='pending').count()
    rejected_products = products.filter(product_status='rejected').count()
    
    # Get total sales and earnings
    seller_orders = OrderItem.objects.filter(product__seller=request.user)
    total_sales = seller_orders.aggregate(total=Sum('quantity'))['total'] or 0
    total_earnings = seller_orders.aggregate(total=Sum('subtotal'))['total'] or 0
    
    # Update seller stats
    seller.total_products = products.count()
    seller.total_sales = total_sales
    seller.total_earnings = total_earnings
    seller.save()
    
    context = {
        'seller': seller,
        'products': products.order_by('-created_at'),
        'total_products': products.count(),
        'approved_products': approved_products,
        'pending_products': pending_products,
        'rejected_products': rejected_products,
        'total_sales': total_sales,
        'total_earnings': total_earnings,
        'average_rating': seller.rating,
    }
    return render(request, 'seller_dashboard.html', context)


@login_required(login_url='app:login')
def upload_product(request):
    """Upload product for sale - Updated to require seller profile"""
    # Check if user is a seller
    try:
        seller = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.error(request, '❌ You must be a registered seller to upload products.')
        return redirect('app:become_seller')
    
    if request.method == 'POST':
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.is_user_uploaded = True
            product.product_status = 'pending'  # Wait for admin approval
            product.save()
            
            messages.success(request, f'✅ Product "{product.name}" uploaded successfully!\n\nIt is pending admin review. Check your seller dashboard for updates.')
            return redirect('app:seller_dashboard')
    else:
        form = ProductUploadForm()
    
    context = {
        'form': form,
        'seller': seller
    }
    return render(request, 'upload_product.html', context)


# ===== SETTINGS PAGE =====

@login_required(login_url='app:login')
def settings_view(request):
    """User settings page"""
    if request.method == 'POST':
        # Handle location update
        try:
            profile = request.user.profile
        except:
            profile = UserProfile.objects.create(user=request.user)
        
        # Update location fields
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.pincode = request.POST.get('pincode', '')
        profile.country = request.POST.get('country', 'India')
        profile.save()
        
        messages.success(request, '✓ Location updated successfully!')
        return redirect('app:settings')
    
    context = {
        'user': request.user
    }
    return render(request, 'settings.html', context)


def update_bank_details(request):
    """Update seller bank details for payment settlements"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in'}, status=401)
    
    if not hasattr(request.user, 'seller_profile'):
        return JsonResponse({'success': False, 'error': 'You are not registered as a seller'}, status=400)
    
    if request.method == 'POST':
        try:
            seller = request.user.seller_profile
            seller.account_holder_name = request.POST.get('account_holder_name', '')
            seller.bank_name = request.POST.get('bank_name', '')
            seller.account_number = request.POST.get('account_number', '')
            seller.ifsc_code = request.POST.get('ifsc_code', '')
            seller.branch_name = request.POST.get('branch_name', '')
            seller.bank_verified = False  # Will be verified by admin
            seller.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Bank details saved successfully! Admin will verify and activate shortly.'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required(login_url='app:login')
def notifications_list(request):
    """Display all notifications for user"""
    notifications = request.user.notifications.all()
    context = {'notifications': notifications}
    return render(request, 'notifications.html', context)


@login_required(login_url='app:login')
def mark_notification_read(request, notif_id):
    """Mark a notification as read"""
    from .models import Notification
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='app:login')
def ai_chat(request):
    """AI-based chat support with product knowledge"""
    from .models import ChatMessage
    
    user_products = Product.objects.filter(seller=request.user) if request.user.seller_profile else None
    user_orders = Order.objects.filter(user=request.user) if request.user.is_authenticated else None
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        message_text = request.POST.get('message', '').strip()
        
        if message_text:
            # Save user message
            product = None
            if product_id:
                product = get_object_or_404(Product, id=product_id)
            
            ChatMessage.objects.create(
                user=request.user,
                product=product,
                message=message_text,
                is_user=True
            )
            
            # Generate AI response
            ai_response = generate_ai_response(request.user, product, message_text)
            ChatMessage.objects.create(
                user=request.user,
                product=product,
                message=ai_response,
                is_user=False
            )
            
            return redirect('app:ai_chat')
    
    # Get chat history for the user
    product_id = request.GET.get('product_id')
    if product_id:
        chat_history = ChatMessage.objects.filter(user=request.user, product_id=product_id)
        current_product = get_object_or_404(Product, id=product_id)
    else:
        chat_history = ChatMessage.objects.filter(user=request.user)
        current_product = None
    
    context = {
        'chat_history': chat_history,
        'current_product': current_product,
        'user_products': user_products,
        'user_orders': user_orders,
    }
    return render(request, 'ai_chat.html', context)


def generate_ai_response(user, product, message):
    """Generate AI response based on user message and product context"""
    # Build context for AI
    context_info = f"User: {user.first_name} {user.last_name}\n"
    
    if product:
        context_info += f"Product: {product.name}\nPrice: ₹{product.price}\nCategory: {product.category}\n"
        if product.description:
            context_info += f"Description: {product.description}\n"
    
    # Get user's orders for context
    orders = Order.objects.filter(user=user).count()
    context_info += f"Total Orders: {orders}\n"
    
    # Simple AI response generator (can integrate with ChatGPT API later)
    # For now, providing intelligent responses based on keywords
    message_lower = message.lower()
    
    # Product-related questions
    if product:
        if 'price' in message_lower or 'cost' in message_lower:
            return f"This {product.name} is priced at ₹{product.price}. " \
                   f"Quality level: {product.quality}. Would you like to add it to your cart?"
        elif 'delivery' in message_lower or 'shipping' in message_lower:
            return f"We provide fast shipping for all products including {product.name}. " \
                   f"Delivery typically takes 2-5 business days depending on your location."
        elif 'warranty' in message_lower or 'guarantee' in message_lower:
            if product.warranty_provided:
                return f"Yes! {product.name} comes with {product.warranty_days} days warranty. " \
                       f"This covers manufacturing defects and ensures product quality."
            else:
                return f"{product.name} is sold as-is. However, we ensure quality and you can return it within 7 days if unsatisfied."
        elif 'stock' in message_lower or 'available' in message_lower:
            if product.stock > 0:
                return f"Good news! {product.name} is in stock with {product.stock} units available. " \
                       f"Get it now before stock runs out!"
            else:
                return f"Unfortunately, {product.name} is currently out of stock. " \
                       f"Would you like us to notify you when it's back in stock?"
    
    # General help questions
    if 'order' in message_lower:
        return "I can help you with your orders! Do you want to:\n1. Track an existing order\n2. Place a new order\n3. Return or exchange a product\n4. Check order status"
    elif 'payment' in message_lower or 'pay' in message_lower:
        return "We accept multiple payment methods:\n• Credit/Debit Card\n• UPI Payment\n• Cash on Delivery\nWhich method would you prefer?"
    elif 'return' in message_lower or 'refund' in message_lower:
        return "We offer 7-day returns and exchanges! To initiate a return:\n1. Go to your orders\n2. Select the product\n3. Choose 'Return/Exchange'\n4. Provide reason and details\nOur team will process it within 24 hours."
    elif 'help' in message_lower or 'support' in message_lower:
        return "I'm here to help! I can assist you with:\n• Product information\n• Order tracking\n• Returns & exchanges\n• Payment issues\n• Delivery information\n\nWhat do you need help with?"
    
    # Default response
    return "Thank you for reaching out! I'm an AI assistant here to help you with your shopping experience. " \
           "I can help with product information, orders, payments, and returns. What can I help you with today?"


def help_center(request):
    """Help center / FAQ page"""
    context = {}
    return render(request, 'help_center.html', context)

