from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.db.models.functions import Lower
from datetime import datetime
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.conf import settings
from django import forms
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Category, News, Contact, FooterContent
from .forms import ContactForm, NewsAdminForm, CategoryAdminForm

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_categories():
    return Category.objects.all()

def get_footer_content(request):
    footer_content = FooterContent.objects.first()
    if not footer_content:
        # Create default footer content if none exists
        footer_content = FooterContent.objects.create(
            site_name='INFO_KAZ',
            copyright_text='© 2025 info-kaz.kz',
            registration_info='Свидетельство о регистрации СМИ №KZ21-12345 от 01.06.2025 г.',
            editor_info='Главный редактор: Иванов И.И.'
        )
    return {'footer_content': footer_content}

def index(request):
    search_query = request.GET.get('search', '')
    
    # Get the News of the Day, exclude deleted
    news_of_the_day = News.objects.filter(is_news_of_the_day=True, is_published=True, is_deleted=False).first()

    # Get other news, exclude News of the Day and deleted
    news_list = News.objects.filter(is_published=True, is_deleted=False).exclude(is_news_of_the_day=True).order_by('-created_at')
    
    if search_query:
        # Convert search_query to lower case for case-insensitive comparison
        search_query_lower = search_query.lower()
        news_list = news_list.filter(
            Q(title__icontains=search_query_lower) |
            Q(content__icontains=search_query_lower)
        )
    
    news_list = news_list[:10] # Apply slice after filtering (or not filtering if search_query is empty)
    
    categories = Category.objects.all()
    context = {
        'news_of_the_day': news_of_the_day, # Pass News of the Day
        'news_list': news_list, # Pass other news
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'news/index.html', context)

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    news_list = News.objects.filter(category=category, is_published=True, is_deleted=False).order_by('-created_at') # Exclude deleted news
    
    search_query = request.GET.get('search', '')
    date_filter = request.GET.get('date_filter', '')
    
    if search_query:
        news_list = news_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    if date_filter:
        news_list = news_list.filter(created_at__date=date_filter)
    
    # Add pagination for category view
    paginator = Paginator(news_list, 5) # Show 5 news per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    available_dates = News.objects.filter(
        category=category,
        is_published=True
    ).dates('created_at', 'day', order='DESC')
    
    categories = Category.objects.all()
    context = {
        'category': category,
        'page_obj': page_obj, # Pass the Page object
        'search_query': search_query,
        'date_filter': date_filter,
        'available_dates': available_dates,
        'categories': categories,
    }
    return render(request, 'news/category_detail.html', context)

def news_detail(request, news_slug):
    # Allow preview of deleted news for admin users
    if request.user.is_staff and request.GET.get('preview_deleted') == 'True':
        news = get_object_or_404(News, slug=news_slug) # Get news regardless of published/deleted status
    else:
        news = get_object_or_404(News, slug=news_slug, is_published=True, is_deleted=False)
    
    # Increment views count only for regular views, once per session
    # Check if the 'viewed_news' list exists in the session, create if not
    viewed_news_list = request.session.get('viewed_news', [])

    # Check if the current news slug is in the viewed list
    if not (request.user.is_staff and request.GET.get('preview_deleted') == 'True') and news.slug not in viewed_news_list:
        news.views_count = F('views_count') + 1
        news.save()
        # Add the news slug to the viewed list in session
        viewed_news_list.append(news.slug)
        request.session['viewed_news'] = viewed_news_list
        request.session.modified = True # Mark session as modified
        
        # Refresh the object from DB after incrementing F() expression
        news.refresh_from_db()
    
    # Get 5 random recommended news (excluding the current one)
    recommended_news = News.objects.filter(
        is_published=True # Consider all published news for randomness
    ).exclude(slug=news_slug).order_by('?')[:5] # Get 5 random news

    categories = Category.objects.all()
    context = {
        'news': news,
        'recommended_news': recommended_news, # Add recommended news to context
        'categories': categories,
    }
    return render(request, 'news/news_detail.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('news:contact_success')
    else:
        form = ContactForm()
    
    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'news/contact.html', context)

def contact_success(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'news/contact_success.html', context)

@staff_member_required
def admin_news_list(request):
    news_list = News.objects.filter(is_deleted=False).order_by('-created_at') # Show only non-deleted news

    # Apply category filter
    category_slug = request.GET.get('category')
    if category_slug:
        news_list = news_list.filter(category__slug=category_slug)

    # Apply search filter
    search_query = request.GET.get('search')
    if search_query:
        news_list = news_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    context = {
        'news_list': news_list,
        'categories': Category.objects.all(), # Для навигации и фильтра
    }
    return render(request, 'news/admin/news_list.html', context)

@staff_member_required
def admin_news_create(request):
    if request.method == 'POST':
        print("POST received")
        print("FILES:", request.FILES)
        form = NewsAdminForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")
            news_item = form.save()
            print("News saved:", news_item)
            print("News image:", news_item.image)
            return redirect(reverse('news:admin_news_list'))
    else:
        form = NewsAdminForm()
        print("Form errors:", form.errors)
    
    context = {
        'form': form,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/news_form.html', context)

@staff_member_required
def admin_news_update(request, news_slug):
    news_item = get_object_or_404(News, slug=news_slug)
    if request.method == 'POST':
        form = NewsAdminForm(request.POST, request.FILES, instance=news_item)
        if form.is_valid():
            form.save()
            return redirect(reverse('news:admin_news_list'))
    else:
        form = NewsAdminForm(instance=news_item)
    
    context = {
        'form': form,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/news_form.html', context)

@staff_member_required
def admin_news_delete(request, news_slug):
    news_item = get_object_or_404(News, slug=news_slug)
    if request.method == 'POST':
        news_item.is_deleted = True # Mark as deleted instead of deleting
        news_item.save() # Save the change
        messages.success(request, f'Новость "{news_item.title}" перемещена в корзину.') # Add a success message
        return redirect(reverse('news:admin_news_list'))
    
    context = {
        'news_item': news_item,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/news_confirm_delete.html', context)

@staff_member_required
def admin_news_trash(request):
    deleted_news = News.objects.filter(is_deleted=True).order_by('-created_at')
    context = {
        'deleted_news': deleted_news,
        'categories': Category.objects.all(), # Для навигации админки
    }
    return render(request, 'news/admin/news_trash.html', context)

@staff_member_required
def admin_news_restore(request, news_slug):
    news_item = get_object_or_404(News.objects.filter(is_deleted=True), slug=news_slug) # Get only deleted news
    if request.method == 'POST':
        news_item.is_deleted = False # Mark as not deleted
        news_item.save()
        messages.success(request, f'Новость "{news_item.title}" успешно восстановлена.')
        return redirect(reverse('news:admin_news_trash')) # Redirect back to trash
    # For GET request, maybe show a confirmation page? Or just handle POST?
    # For simplicity, we'll just handle POST here, confirmation can be in template
    return redirect(reverse('news:admin_news_trash')) # Redirect back to trash for GET

# Custom Admin Views for Categories
@staff_member_required
def admin_category_list(request):
    categories_list = Category.objects.all().order_by('name')
    context = {
        'categories_list': categories_list,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/category_list.html', context)

@staff_member_required
def admin_category_create(request):
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('news:admin_category_list'))
    else:
        form = CategoryAdminForm()
    
    context = {
        'form': form,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/category_form.html', context)

@staff_member_required
def admin_category_update(request, category_slug):
    category_item = get_object_or_404(Category, slug=category_slug)
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST, instance=category_item)
        if form.is_valid():
            form.save()
            return redirect(reverse('news:admin_category_list'))
    else:
        form = CategoryAdminForm(instance=category_item)
    
    context = {
        'form': form,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/category_form.html', context)

@staff_member_required
def admin_category_delete(request, category_slug):
    category_item = get_object_or_404(Category, slug=category_slug)
    if request.method == 'POST':
        category_item.delete()
        return redirect(reverse('news:admin_category_list'))
    
    context = {
        'category_item': category_item,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/category_confirm_delete.html', context)

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                auth_login(request, user)
                # Перенаправление на страницу списка новостей в админке
                return redirect(reverse('news:admin_news_list'))
            else:
                # Возможно, добавить сообщение об ошибке для не-персонала
                pass # Пока просто оставим без перенаправления
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'categories': Category.objects.all(), # Для навигации
    }
    return render(request, 'news/admin/login.html', context)

@staff_member_required
def admin_contact_list(request):
    status = request.GET.get('status')
    if status == 'unread':
        messages = Contact.objects.filter(status='new').order_by('-created_at')
    elif status == 'read':
        messages = Contact.objects.filter(status='read').order_by('-created_at')
    else:
        messages = Contact.objects.all().order_by('-created_at')
    
    unread_count = Contact.objects.filter(status='new').count()
    
    context = {
        'messages': messages,
        'unread_messages_count': unread_count,
    }
    return render(request, 'news/admin/contact_list.html', context)

@staff_member_required
def admin_contact_detail(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    context = {
        'message': message,
        'unread_messages_count': Contact.objects.filter(status='new').count(),
    }
    return render(request, 'news/admin/contact_detail.html', context)

@staff_member_required
def admin_contact_delete(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Сообщение успешно удалено')
        return redirect('news:admin_contact_list')
    return render(request, 'news/admin/contact_confirm_delete.html', {'message': message})

@staff_member_required
def admin_contact_mark_read(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    if request.method == 'POST':
        message.status = 'read'
        message.save()
        messages.success(request, 'Сообщение отмечено как прочитанное')
    return redirect('news:admin_contact_detail', message_id=message.id)

@staff_member_required
def admin_dashboard(request):
    # Get some statistics for the dashboard
    total_news_count = News.objects.filter(is_deleted=False).count()
    total_categories_count = Category.objects.count()
    total_messages_count = Contact.objects.count()
    unread_messages_count = Contact.objects.filter(status='new').count()
    published_news_count = News.objects.filter(is_published=True, is_deleted=False).count()
    deleted_news_count = News.objects.filter(is_deleted=True).count()

    context = {
        'total_news_count': total_news_count,
        'total_categories_count': total_categories_count,
        'total_messages_count': total_messages_count,
        'unread_messages_count': unread_messages_count,
        'published_news_count': published_news_count,
        'deleted_news_count': deleted_news_count,
        'categories': Category.objects.all(), # Для навигации админки
    }
    return render(request, 'news/admin/admin_dashboard.html', context)

@staff_member_required
def admin_news_of_the_day(request):
    if request.method == 'POST':
        news_slug = request.POST.get('news_slug')
        if news_slug:
            # Unset the previous News of the Day
            News.objects.filter(is_news_of_the_day=True).update(is_news_of_the_day=False)
            # Set the new News of the Day
            news_item = get_object_or_404(News, slug=news_slug)
            news_item.is_news_of_the_day = True
            news_item.save()
            messages.success(request, f'"{news_item.title}" назначена новостью дня.')
        else:
             # If no news_slug is provided in POST, it means we want to unset the current News of the Day
            News.objects.filter(is_news_of_the_day=True).update(is_news_of_the_day=False)
            messages.success(request, 'Новость дня снята.')
        return redirect(reverse('news:admin_news_of_the_day'))

    news_list = News.objects.filter(is_deleted=False).order_by('-created_at') # Show non-deleted news
    current_news_of_the_day = News.objects.filter(is_news_of_the_day=True, is_deleted=False).first()

    context = {
        'news_list': news_list,
        'current_news_of_the_day': current_news_of_the_day,
        'categories': Category.objects.all(), # Для навигации админки
    }
    return render(request, 'news/admin/news_of_the_day.html', context)

@staff_member_required
def admin_footer_edit(request):
    footer_content = FooterContent.objects.first()
    if not footer_content:
        footer_content = FooterContent.objects.create(
            site_name='INFO_KAZ',
            site_name_font_size='1.2rem',
            copyright_text='© 2025 info-kaz.kz',
            copyright_text_font_size='0.9rem',
            registration_info='Свидетельство о регистрации СМИ №KZ21-12345 от 01.06.2025 г.',
            registration_info_font_size='0.9rem',
            editor_info='Главный редактор: Иванов И.И.',
            editor_info_font_size='0.9rem',
            extra_fields={}
        )

    if request.method == 'POST':
        footer_content.site_name = request.POST.get('site_name')
        footer_content.site_name_font_size = f"{request.POST.get('site_name_font_size', '1.2')}rem"
        footer_content.copyright_text = request.POST.get('copyright_text')
        footer_content.copyright_text_font_size = f"{request.POST.get('copyright_text_font_size', '0.9')}rem"
        footer_content.registration_info = request.POST.get('registration_info')
        footer_content.registration_info_font_size = f"{request.POST.get('registration_info_font_size', '0.9')}rem"
        footer_content.editor_info = request.POST.get('editor_info')
        footer_content.editor_info_font_size = f"{request.POST.get('editor_info_font_size', '0.9')}rem"

        # Обработка дополнительных полей (теперь включает размер шрифта)
        extra_fields_data = {}
        for key, value in request.POST.items():
            if key.startswith('extra_field_key_'):
                index = key.replace('extra_field_key_', '')
                field_key = value # Ключ дополнительного поля
                field_value = request.POST.get(f'extra_field_value_{index}', '') # Значение
                field_font_size = f"{request.POST.get(f'extra_field_font_size_{index}', '0.9')}rem" # Размер шрифта
                if field_key:
                     extra_fields_data[field_key] = {'text': field_value, 'font_size': field_font_size}

        footer_content.extra_fields = extra_fields_data

        footer_content.save()
        messages.success(request, 'Футер успешно обновлен')
        return redirect('news:admin_footer_edit')

    # Determine whether to show optional fields
    show_registration_info_input = bool(footer_content.registration_info) or (request.method == 'POST' and request.POST.get('registration_info') is not None)
    show_editor_info_input = bool(footer_content.editor_info) or (request.method == 'POST' and request.POST.get('editor_info') is not None)

    # Convert font sizes from 'rem' to numbers for the form
    def strip_rem(value):
        return value.replace('rem', '') if value else '0.9'

    # Prepare font sizes for display in the form
    font_sizes_display = {
        'site_name_font_size': strip_rem(footer_content.site_name_font_size),
        'copyright_text_font_size': strip_rem(footer_content.copyright_text_font_size),
        'registration_info_font_size': strip_rem(footer_content.registration_info_font_size),
        'editor_info_font_size': strip_rem(footer_content.editor_info_font_size),
    }

    context = {
        'footer_content': footer_content,
        'categories': Category.objects.all(),
        # Передача дополнительных полей в удобном формате для шаблона
        'extra_fields_list': [(key, value['text'], strip_rem(value.get('font_size', '0.9rem'))) for key, value in footer_content.extra_fields.items()], # Use .get with default for safety
        'show_registration_info_input': show_registration_info_input,
        'show_editor_info_input': show_editor_info_input,
        'font_sizes_display': font_sizes_display, # Pass numeric font sizes for display
    }
    return render(request, 'news/admin/footer_edit.html', context) 