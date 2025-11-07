# В файле rss_feeds/migrations/0002_auto_... (твой файл)
# ... другие импорты ...
from django.db import migrations
import json
import os
from django.conf import settings

# Получаем путь к файлу initial_rss_feeds.json, относительно корня проекта
file_path = os.path.join(settings.BASE_DIR, 'initial_rss_feeds.json')

# Загружаем данные из файла, используя абсолютный путь
with open(file_path, 'r', encoding='utf-8') as f:
    initial_data = json.load(f)

def load_initial_data(apps, schema_editor):
    RSSFeed = apps.get_model('rss_feeds', 'RSSFeed')
    RSSFeed.objects.bulk_create([RSSFeed(**item['fields']) for item in initial_data], ignore_conflicts=True)

def reverse_func(apps, schema_editor):
    RSSFeed = apps.get_model('rss_feeds', 'RSSFeed')
    urls_to_delete = [item['fields']['url'] for item in initial_data]
    RSSFeed.objects.filter(url__in=urls_to_delete).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rss_feeds', '0001_initial'), # <-- Вот она, зависимость от 0001
    ]

    operations = [
        migrations.RunPython(load_initial_data, reverse_func),
    ]
