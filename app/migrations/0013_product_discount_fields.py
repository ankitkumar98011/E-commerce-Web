from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0012_alter_ordertracking_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount_price',
            field=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text='Discounted price (if any)'),
        ),
        migrations.AddField(
            model_name='product',
            name='is_discounted',
            field=models.BooleanField(default=False, help_text='Is product currently discounted?'),
        ),
    ]
