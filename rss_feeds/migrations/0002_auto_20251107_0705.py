# rss_feeds/migrations/0003_auto_20251107_1234.py (замените на реальное имя файла)
from django.db import migrations
import json # Импортируем json

# Загружаем данные из файла
with open('initial_rss_feeds.json', 'r', encoding='utf-8') as f:
    initial_data = json.load(f)

def load_initial_data(apps, schema_editor):
    RSSFeed = apps.get_model('rss_feeds', 'RSSFeed')
    # Используем bulk_create для эффективного добавления
    RSSFeed.objects.bulk_create([RSSFeed(**item['fields']) for item in initial_data], ignore_conflicts=True)

def reverse_func(apps, schema_editor):
    RSSFeed = apps.get_model('rss_feeds', 'RSSFeed')
    # Удаляем данные при откате миграции (опционально)
    urls_to_delete = [item['fields']['url'] for item in initial_data]
    RSSFeed.objects.filter(url__in=urls_to_delete).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rss_feeds', '0001'), # <-- ЗАМЕНИТЕ '0002' НА ПРЕДЫДУЩУЮ МИГРАЦИЮ
    ]

    operations = [
        migrations.RunPython(load_initial_data, reverse_func),
    ]
