"""
Sitemaps для SEO. Используется django.contrib.sitemaps.
Файл доступен по адресу: https://www.info-kaz.kz/sitemap.xml
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import News, Category


class NewsSitemap(Sitemap):
    """Карта сайта для новостей."""
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return News.objects.filter(is_published=True, is_deleted=False).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    """Карта сайта для категорий."""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('news:category_detail', args=[obj.slug])


class StaticSitemap(Sitemap):
    """Статические страницы."""
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['news:index', 'news:contact']

    def location(self, obj):
        return reverse(obj)
