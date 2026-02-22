from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0010_product_warranty_days_product_warranty_provided_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=20)),
                ('location', models.CharField(blank=True, default='', max_length=255)),
                ('details', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracking_updates', to='app.order')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]
