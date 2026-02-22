from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products_list, name='products'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('api/personalized-recommendations/', views.get_personalized_recommendations, name='personalized_recommendations'),
    path('api/hybrid-recommendations/', views.get_hybrid_recommendations, name='hybrid_recommendations'),
    path('api/track-interaction/', views.track_interaction, name='track_interaction'),
    
    # Seller System
    path('become-seller/', views.become_seller, name='become_seller'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),
    
    # Product Upload & Management
    path('upload-product/', views.upload_product, name='upload_product'),
    path('my-products/', views.my_products, name='my_products'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Shopping Cart & Checkout
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('api/verify-payment/<int:order_id>/', views.verify_payment, name='verify_payment'),
    path('api/payment-callback/', views.payment_callback, name='payment_callback'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:order_id>/return/', views.request_return, name='request_return'),
    path('order/<int:order_id>/invoice/', views.invoice_view, name='invoice_view'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('help/', views.help_center, name='help_center'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('notification/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('api/update-bank-details/', views.update_bank_details, name='update_bank_details'),
]