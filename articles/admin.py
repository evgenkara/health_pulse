# articles/admin.py
from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'published_at', 'source_name') # Добавили source_name в список
    list_filter = ('category', 'is_published', 'published_at', 'source_name') # Добавили фильтр по источнику
    search_fields = ('title', 'original_content', 'source_name') # Добавили поиск по источнику
    readonly_fields = ('published_at',)
    # Убираем author, добавляем source_name
    fields = ('title', 'original_content', 'processed_content', 'summary', 'source_url', 'source_name', 'image_url', 'tags', 'category', 'is_published', 'slug')
