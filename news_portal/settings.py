"""
Django settings for news_portal project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные из .env файла (если он существует)
load_dotenv(BASE_DIR / '.env')

# Без .env — всё из окружения DigitalOcean
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = [
    'info-kaz-final.onrender.com',
    'info-kaz.kz',
    'www.info-kaz.kz',
    '127.0.0.1',
    'localhost',
]

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'ckeditor',
    'ckeditor_uploader',
    'storages',
    'widget_tweaks',
    'news.apps.NewsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'news_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'news.views.get_footer_content',
            ],
        },
    },
]

WSGI_APPLICATION = 'news_portal.wsgi.application'

# База данных
import dj_database_url

# Автодетект пула Supabase: при использовании pooler лучше держать conn_max_age = 0,
# чтобы соединения не оставались висящими и не забивали ограниченный пул.
_database_url = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3')
_is_supabase_pooler = 'pooler.' in _database_url or 'pooler.supabase' in _database_url
_default_conn_max_age = 0 if _is_supabase_pooler else int(os.environ.get('DB_CONN_MAX_AGE', '600'))

DATABASES = {
    'default': dj_database_url.parse(
        _database_url,
        conn_max_age=_default_conn_max_age,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# Валидация пароля
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

# Статика
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'news', 'static')]
# WhiteNoise: сжатие и хэш-имена для бесконечного кеширования
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Явный max-age для статики, если понадобится (секунды)
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 365  # 1 год

# Supabase Storage
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://khlfpcspkgttuckedlfy.supabase.co')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
# Optional: service role key for server-side writes (recommended)
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

# Настройки для Supabase Storage (прямой API)
DEFAULT_FILE_STORAGE = 'news_portal.storage_backends.MediaStorage'
MEDIA_URL = f"{SUPABASE_URL}/storage/v1/object/public/media/"
MEDIA_ROOT = ''

# CKEditor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_STORAGE_BACKEND = 'news_portal.storage_backends.MediaStorage'
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_DATE = True
CKEDITOR_FORCE_JPEG_COMPRESSION = True
CKEDITOR_IMAGE_QUALITY = 90
CKEDITOR_THUMBNAIL_SIZE = (300, 300)
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar_Basic': [['Source', '-', 'Bold', 'Italic']],
        'toolbar_Full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'],
            ['Source'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList'],
            ['Indent', 'Outdent'],
            ['Maximize'],
        ],
        'toolbar': 'Full',
        'height': 500,
        'width': '100%',
        'filebrowserWindowHeight': 725,
        'filebrowserWindowWidth': 940,
        'toolbarCanCollapse': True,
    },
}

# Авторизация
LOGIN_URL = 'news:admin_login'

# Безопасность
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_SSL_REDIRECT_EXEMPT = [r'^__debug__/.*$']
X_FRAME_OPTIONS = 'ALLOWALL'

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'INFO',
    },
}

# Увеличим допустимые размеры загрузок (на случай видео/крупных изображений)
# Значения в байтах: 50 MB и 100 MB соответственно
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
