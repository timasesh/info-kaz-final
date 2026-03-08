"""
URL configuration for news_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from ckeditor_uploader import views as ckeditor_views
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from news.sitemaps import NewsSitemap, CategorySitemap, StaticSitemap

sitemaps = {
    'news': NewsSitemap,
    'categories': CategorySitemap,
    'static': StaticSitemap,
}


@require_GET
def robots_txt(request):
    """Служит robots.txt для поисковых систем."""
    lines = [
        'User-agent: *',
        'Allow: /',
        'Sitemap: https://www.info-kaz.kz/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')


urlpatterns = [
    path('', include('news.urls')),
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt),
    # CKEditor URLs with updated patterns
    path('ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(login_required(ckeditor_views.browse)), name='ckeditor_browse'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
