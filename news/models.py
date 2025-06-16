from django.db import models
from django.utils.text import slugify
from django.db.models import Max
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.json import JSONField
from ckeditor_uploader.fields import RichTextUploadingField
from news_portal.storage_backends import MediaStorage

def get_storage_object():
    """Returns a configured storage backend instance for handling file uploads."""
    return MediaStorage()

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name='URL-слаг')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug_exists = True
            counter = 1
            while slug_exists:
                slug = base_slug
                if counter > 1:
                    slug = f'{base_slug}-{counter}'
                if not Category.objects.filter(slug=slug).exists():
                    self.slug = slug
                    slug_exists = False
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

def news_image_path(instance, filename):
    """
    Returns consistent path structure for news images
    Format: news-images/YYYY/MM/DD/filename
    
    This path is used directly without media/ prefix since news images 
    are stored separately from CKEditor uploads
    """
    now = timezone.now()
    # Clean the filename to ensure it's URL safe
    from urllib.parse import quote
    safe_filename = quote(filename)
    
    # Always return just the relative path - the storage backend will handle the full path
    return f'news-images/{now.year}/{now.month:02d}/{now.day:02d}/{safe_filename}'

class News(models.Model):    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = RichTextUploadingField(verbose_name='Текст новости', config_name='default')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')    
    image = models.ImageField(
        upload_to=news_image_path, 
        verbose_name='Изображение', 
        null=True, 
        blank=True,
        storage=get_storage_object()
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='news', verbose_name='Категория')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалено')
    views_count = models.IntegerField(default=0, verbose_name='Количество просмотров')
    slug = models.SlugField(max_length=200, unique=True, db_index=True, verbose_name='URL-слаг')
    is_news_of_the_day = models.BooleanField(default=False, verbose_name='Новость дня')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            # Если slugify вернул пустую строку, используем значение по умолчанию
            if not base_slug:
                 base_slug = 'article'

            slug = base_slug
            counter = 1
            # Проверяем уникальность среди объектов News, исключая текущий объект (для обновлений)
            # Используем loop для поиска уникального слага
            while News.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Contact(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('in_progress', 'В обработке'),
        ('completed', 'Завершено'),
    ]

    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=200, verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    admin_response = models.TextField(verbose_name='Ответ администратора', blank=True, null=True)
    response_date = models.DateTimeField(verbose_name='Дата ответа', blank=True, null=True)

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class FooterContent(models.Model):
    site_name = models.CharField(_('Название сайта'), max_length=100)
    site_name_font_size = models.CharField(_('Размер шрифта Названия сайта'), max_length=20, default='1.2rem', help_text=_('Например: 16px, 1.2em, 1.5rem'))
    copyright_text = models.CharField(_('Текст копирайта'), max_length=200)
    copyright_text_font_size = models.CharField(_('Размер шрифта Текста копирайта'), max_length=20, default='0.9rem', help_text=_('Например: 14px, 0.9em, 0.8rem'))
    registration_info = models.CharField(_('Информация о регистрации'), max_length=200, blank=True, null=True)
    registration_info_font_size = models.CharField(_('Размер шрифта Информации о регистрации'), max_length=20, default='0.9rem', blank=True, help_text=_('Например: 14px, 0.9em, 0.8rem'))
    editor_info = models.CharField(_('Информация о редакторе'), max_length=200, blank=True, null=True)
    editor_info_font_size = models.CharField(_('Размер шрифта Информации о редакторе'), max_length=20, default='0.9rem', blank=True, help_text=_('Например: 14px, 0.9em, 0.8rem'))
    extra_fields = JSONField(_('Дополнительные поля (текст и размер шрифта)'), default=dict, blank=True)
    updated_at = models.DateTimeField(_('Последнее обновление'), auto_now=True)

    class Meta:
        verbose_name = _('Содержимое футера')
        verbose_name_plural = _('Содержимое футера')

    def __str__(self):
        return f"Footer Content - {self.updated_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.pk and FooterContent.objects.exists():
            # If this is the first object and there are existing objects,
            # don't create a new one
            return
        super().save(*args, **kwargs)


from django.db import models
from django.contrib.auth.models import User

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='Пользователь')
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='likes', verbose_name='Новость')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата лайка')

    class Meta:
        unique_together = ('user', 'news')
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f"{self.user} лайкнул {self.news}"

