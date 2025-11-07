# rss_feeds/models.py
from django.db import models

# Определяем возможные категории для RSS-ленты
CATEGORIES = [
    ('medicine', 'Medicine'),
    ('fitness', 'Fitness'),
    ('nutrition', 'Nutrition'),
    ('lifestyle', 'Lifestyle'),
]

class RSSFeed(models.Model):
    url = models.URLField(unique=True, help_text="URL RSS-ленты")
    category = models.CharField(max_length=50, choices=CATEGORIES, help_text="Категория, в которую будут помещаться статьи из этой ленты")
    is_active = models.BooleanField(default=True, help_text="Активна ли лента для опроса")
    last_fetched = models.DateTimeField(null=True, blank=True, help_text="Время последнего опроса ленты")
    fetch_frequency = models.IntegerField(default=30, help_text="Частота опроса ленты в минутах") # 30 минут по умолчанию

    def __str__(self):
        return f"{self.url} ({self.get_category_display()})"

    class Meta:
        verbose_name = "RSS Feed"
        verbose_name_plural = "RSS Feeds"
