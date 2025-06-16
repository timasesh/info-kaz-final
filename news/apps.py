from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    path = 'news'  # Укажите точный путь к директории приложения

# Указанный путь к приложению корректный, так как он соответствует структуре вашего проекта,
# где основная директория проекта и директория с manage.py называются "news_portal".
