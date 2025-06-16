from django.contrib import admin
from django.utils.html import format_html
from .models import Category, News, Contact, FooterContent
from .forms import NewsAdminForm

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ('title', 'category', 'created_at', 'is_published')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    fieldsets = (
        (None, {'fields': ('name', 'email', 'subject', 'message', 'created_at')}),
        ('Статус и ответ', {'fields': ('status', 'admin_response', 'response_date')}),
    )

@admin.register(FooterContent)
class FooterContentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False

    def preview_footer(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">'
            '<h3 style="margin-bottom: 10px;">{}</h3>'
            '<p>{}</p>'
            '<p>{}</p>'
            '<p style="text-align: right;">{}</p>'
            '</div>',
            obj.site_name,
            obj.copyright_text,
            obj.registration_info,
            obj.editor_info
        )
    preview_footer.short_description = 'Предпросмотр футера'

    fieldsets = (
        ('Предпросмотр', {
            'fields': ('preview_footer',),
            'classes': ('collapse',),
        }),
        ('Редактирование содержимого', {
            'fields': ('site_name', 'copyright_text', 'registration_info', 'editor_info'),
        }),
    )
    readonly_fields = ('preview_footer', 'updated_at')