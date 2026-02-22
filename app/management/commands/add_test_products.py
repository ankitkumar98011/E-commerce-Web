from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Product, SellerProfile
from datetime import datetime


class Command(BaseCommand):
    help = 'Add test products with stock to the database'

    def handle(self, *args, **options):
        # Get or create a test seller
        seller_user, created = User.objects.get_or_create(
            username='test_seller',
            defaults={
                'email': 'seller@test.com',
                'first_name': 'Test',
                'last_name': 'Seller'
            }
        )
        
        seller_profile, created = SellerProfile.objects.get_or_create(
            user=seller_user,
            defaults={
                'shop_name': 'Test Shop',
                'seller_id': 'SELLER001',
                'rating': 4.5
            }
        )

        # Test products data
        test_products = [
            {
                'name': 'Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation',
                'price': 2999.99,
                'stock': 50,
                'category': 'electronics',
                'quality': 'premium'
            },
            {
                'name': 'USB-C Cable',
                'description': 'Durable USB-C charging and data cable',
                'price': 299.99,
                'stock': 100,
                'category': 'electronics',
                'quality': 'standard'
            },
            {
                'name': 'Wireless Mouse',
                'description': 'Ergonomic wireless mouse with precision tracking',
                'price': 799.99,
                'stock': 75,
                'category': 'electronics',
                'quality': 'standard'
            },
            {
                'name': 'Laptop Stand',
                'description': 'Adjustable aluminum laptop stand for better ergonomics',
                'price': 1499.99,
                'stock': 30,
                'category': 'accessories',
                'quality': 'premium'
            },
            {
                'name': 'USB Hub',
                'description': '4-port USB 3.0 hub with fast charging',
                'price': 599.99,
                'stock': 60,
                'category': 'electronics',
                'quality': 'standard'
            },
        ]

        created_count = 0
        for product_data in test_products:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'stock': product_data['stock'],
                    'category': product_data['category'],
                    'quality': product_data['quality'],
                    'product_status': 'approved',
                    'seller': seller_user,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created product: {product.name} (Stock: {product.stock})')
                )
            else:
                # Update stock if product already exists
                if product.stock == 0:
                    product.stock = product_data['stock']
                    product.product_status = 'approved'
                    product.save()
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Updated product: {product.name} (Stock: {product.stock})')
                    )
                else:
                    self.stdout.write(
                        self.style.NOTICE(f'→ Product already exists: {product.name} (Stock: {product.stock})')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created {created_count} new test products!')
        )
        self.stdout.write(self.style.SUCCESS('✓ All products are now visible on the Products page'))
