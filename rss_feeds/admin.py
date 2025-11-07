# rss_feeds/admin.py
from django.contrib import admin
from .models import RSSFeed

@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ('url', 'category', 'is_active', 'last_fetched', 'fetch_frequency')
    list_filter = ('category', 'is_active')
    search_fields = ('url',)
    readonly_fields = ('last_fetched',) # last_fetched обновляется автоматически
