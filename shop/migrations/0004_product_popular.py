# Generated by Django 5.1.7 on 2025-05-09 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_category_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='popular',
            field=models.BooleanField(default=False),
        ),
    ]
