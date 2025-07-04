# Generated by Django 5.2.3 on 2025-06-13 14:41

import news.models
import news_portal.storage_backends
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0016_alter_news_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=news_portal.storage_backends.MediaStorage(), upload_to=news.models.news_image_path, verbose_name='Изображение'),
        ),
    ]
