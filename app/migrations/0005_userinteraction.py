# Generated migration for UserInteraction model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0004_product_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('view', 'Product View'), ('click', 'Product Click'), ('purchase', 'Purchase'), ('rating', 'Product Rating'), ('cart', 'Add to Cart'), ('wishlist', 'Add to Wishlist')], max_length=20)),
                ('rating_value', models.PositiveIntegerField(blank=True, help_text='Rating given by user (1-5)', null=True)),
                ('weight', models.FloatField(default=1.0, help_text='Weight for ML algorithm')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('session_id', models.CharField(blank=True, help_text='Session identifier', max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='app.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='userinteraction',
            index=models.Index(fields=['user', '-timestamp'], name='app_userint_user_id_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='userinteraction',
            index=models.Index(fields=['product', '-timestamp'], name='app_userint_product_id_timestamp_idx'),
        ),
    ]
