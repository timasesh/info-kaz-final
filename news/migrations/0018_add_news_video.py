from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0017_alter_news_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='video',
            field=models.FileField(
                upload_to='news-videos',
                verbose_name='Видео',
                null=True,
                blank=True,
                help_text='Поддерживаются MP4, WebM, MOV',
            ),
        ),
    ]


