from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0013_product_discount_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notif_type', models.CharField(choices=[('order_placed', 'Order Placed'), ('order_shipped', 'Order Shipped'), ('order_delivered', 'Order Delivered'), ('order_cancelled', 'Order Cancelled'), ('product_approved', 'Product Approved'), ('product_rejected', 'Product Rejected'), ('product_sold', 'Product Sold'), ('product_returned', 'Product Returned'), ('custom', 'Custom')], default='custom', max_length=30)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
