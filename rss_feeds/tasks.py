# rss_feeds/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import RSSFeed
from .utils import parse_rss_feed
from articles.models import Article
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_and_store_articles_from_feed(feed_id):
    """
    Celery задача: опрашивает одну RSS-ленту и сохраняет новые статьи в базу данных.
    """
    try:
        feed = RSSFeed.objects.get(id=feed_id)
        if not feed.is_active:
            logger.info(f"Лента {feed.url} неактивна, пропускаем.")
            return

        # Парсим ленту
        articles_data = parse_rss_feed(feed.url)
        if not articles_data:
            logger.info(f"Не удалось получить статьи из ленты {feed.url}")
            return

        new_articles_count = 0
        for article_data in articles_data:
            # Проверяем, существует ли статья с таким URL
            if not Article.objects.filter(source_url=article_data['link']).exists():
                # Создаём новую статью
                Article.objects.create(
                    title=article_data['title'],
                    original_content=article_data['content'], # Используем 'content' из utils
                    summary='', # Пока пусто, заполнит LLM
                    source_url=article_data['link'],
                    source_name=urlparse(feed.url).netloc,
                    published_at=article_data['published_at'] or timezone.now(),
                    category=feed.category,
                    is_published=False,
                    image_url=article_data.get('image_url', None) # Сохраняем изображение, если есть
                )
                new_articles_count += 1
            else:
                logger.debug(f"Статья с URL {article_data['link']} уже существует, пропускаем.")

        # Обновляем время последнего опроса
        feed.last_fetched = timezone.now()
        feed.save()

        logger.info(f"Лента {feed.url}: добавлено {new_articles_count} новых статей.")

    except RSSFeed.DoesNotExist:
        logger.error(f"RSSFeed с id {feed_id} не найден.")
    except Exception as e:
        logger.error(f"Ошибка в задаче fetch_and_store_articles_from_feed для id {feed_id}: {e}")

@shared_task
def fetch_all_active_feeds():
    """
    Celery задача: запускает опрос всех активных RSS-лент.
    """
    logger.info("Запуск опроса всех активных RSS-лент.")
    active_feeds = RSSFeed.objects.filter(is_active=True)

    for feed in active_feeds:
        if feed.last_fetched:
            time_since_last_fetch = timezone.now() - feed.last_fetched
            if time_since_last_fetch.total_seconds() < (feed.fetch_frequency * 60):
                logger.debug(f"Лента {feed.url} опрошена недавно, пропускаем.")
                continue

        fetch_and_store_articles_from_feed.delay(feed.id)

    logger.info("Опрос всех активных RSS-лент завершён.")
