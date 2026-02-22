# Generated migration for SellerProfile model

from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_ecommerce_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='SellerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_id', models.CharField(editable=False, max_length=20, unique=True)),
                ('shop_name', models.CharField(max_length=255)),
                ('shop_description', models.TextField(blank=True)),
                ('shop_image', models.ImageField(blank=True, null=True, upload_to='shops/')),
                ('rating', models.DecimalField(decimal_places=1, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('total_reviews', models.IntegerField(default=0)),
                ('total_products', models.IntegerField(default=0)),
                ('total_sales', models.IntegerField(default=0)),
                ('total_earnings', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('is_verified', models.BooleanField(default=False, help_text='Admin verification status')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='seller_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
