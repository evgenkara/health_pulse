# rss_feeds/utils.py
import feedparser
import logging
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup, NavigableString, Comment
import time
import re # Для очистки текста

logger = logging.getLogger(__name__)

# --- НОВАЯ ФУНКЦИЯ ДЛЯ ОЧИСТКИ HTML ---
def clean_html_element(element):
    """
    Рекурсивно удаляет нежелательные элементы и строки из BeautifulSoup-элемента.
    """
    # Список тегов для удаления (можно расширить)
    unwanted_tags = ['script', 'style', 'aside', 'nav', 'footer', 'header', 'form', 'input', 'button', 'iframe', 'embed', 'object', 'noscript', 'svg']
    # Список классов/ID для удаления (примеры, можно настроить)
    unwanted_classes_ids = ['ad', 'advertisement', 'ads', 'promo', 'social-share', 'comments', 'comment', 'related', 'sidebar', 'widget', 'newsletter', 'subscribe']

    # Удаляем нежелательные теги
    for unwanted_tag in unwanted_tags:
        for tag in element.find_all(unwanted_tag):
            tag.decompose()

    # Удаляем элементы с нежелательными классами/ID
    for class_id in unwanted_classes_ids:
        for tag in element.find_all(attrs={"class": re.compile(f".*{class_id}.*", re.I)}):
            tag.decompose()
        for tag in element.find_all(attrs={"id": re.compile(f".*{class_id}.*", re.I)}):
            tag.decompose()

    # Удаляем комментарии
    for comment in element.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Удаляем пустые элементы
    for tag in element.find_all():
        if not tag.get_text(strip=True):
            tag.decompose()

# --- /НОВАЯ ФУНКЦИЯ ---

def extract_content_from_page(url: str, selectors: list) -> dict:
    """
    Пытается извлечь основной контент статьи и изображение со страницы по URL.

    Args:
        url (str): URL страницы статьи.
        selectors (list): Список CSS-селекторов для поиска основного контента (например, 'article', '.content', '.post-body').

    Returns:
        dict: {'content': str, 'image_url': str or None}. Возвращает пустой словарь в случае ошибки.
    """
    try:
        logger.info(f"Попытка извлечения контента со страницы: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        content_text = ""
        image_url = None

        # --- ПОИСК ОСНОВНОГО КОНТЕНТА ---
        main_content_element = None
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                main_content_element = element
                logger.info(f"Контент найден с помощью селектора '{selector}' из {url}")
                break

        if main_content_element:
            # Очищаем найденный элемент
            clean_html_element(main_content_element)
            # Извлекаем текст
            content_text = main_content_element.get_text(separator=' ', strip=True)
            # Пытаемся извлечь изображение из этого элемента (например, тег <img>)
            img_tag = main_content_element.find('img')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']
                # Если URL относительный, преобразуем в абсолютный
                from urllib.parse import urljoin
                image_url = urljoin(url, image_url)
                logger.debug(f"Изображение найдено в основном контенте: {image_url}")
        else:
            logger.warning(f"Не удалось извлечь основной контент из {url} с помощью предоставленных селекторов.")

        # --- ПОИСК ИЗОБРАЖЕНИЯ В МЕТА-ТЕГАХ (альтернатива) ---
        if not image_url:
            # Пытаемся найти изображение в Open Graph или Twitter Card
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image['content']
                logger.debug(f"Изображение найдено в og:image: {image_url}")
            else:
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image['content']
                    logger.debug(f"Изображение найдено в twitter:image: {image_url}")

        # --- ОЧИСТКА ТЕКСТА ---
        if content_text:
            # Убираем лишние пробелы, символы новой строки, повторяющиеся символы
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            # Убираем часто встречающийся мусор (примеры, можно адаптировать)
            # Например, строки типа "Sign up for our Newsletter"
            content_text = re.sub(r'(?i)sign up for.*?newsletter|subscribe.*?here|click.*?more', '', content_text)
            # Убираем строки, состоящие только из пунктуации или специальных символов (длинные)
            content_text = re.sub(r'^[\W_]+$', '', content_text, flags=re.MULTILINE).strip()

        logger.info(f"Извлечение завершено для {url}. Контент длиной: {len(content_text)}, Изображение: {image_url}")
        return {'content': content_text, 'image_url': image_url}

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к {url}: {e}")
        return {'content': '', 'image_url': None}
    except Exception as e:
        logger.error(f"Ошибка при парсинге страницы {url}: {e}")
        return {'content': '', 'image_url': None}

# --- /ОБНОВЛЁННАЯ ФУНКЦИЯ ---

# --- ОБНОВЛЯЕМ parse_rss_feed ---
from datetime import datetime # Убедимся, что datetime импортирован

def parse_rss_feed(feed_url: str):
    """
    Парсит RSS-ленту по указанному URL и пытается извлечь полный контент и изображение.
    """
    try:
        logger.info(f"Парсинг RSS-ленты: {feed_url}")
        feed = feedparser.parse(feed_url)

        if feed.bozo: # feedparser обнаружил ошибки в формате
            logger.warning(f"Bozo error при парсинге {feed_url}: {feed.bozo_exception}")

        articles = []
        for entry in feed.entries:
            # Извлекаем дату публикации
            published_parsed = getattr(entry, 'published_parsed', None)
            published_at = datetime(*published_parsed[:6]) if published_parsed else None

            # Извлекаем основные поля
            title = getattr(entry, 'title', 'Без заголовка')
            link = getattr(entry, 'link', '')
            description = getattr(entry, 'description', '') # Это может быть краткое содержание или фрагмент HTML

            # --- НОВАЯ ЛОГИКА ---
            content = description # Начинаем с description
            image_url = None # Инициализируем URL изображения

            if not content.strip() or len(content.strip()) < 200: # Если description короткий или пустой
                # Пытаемся извлечь полный текст и изображение со страницы статьи
                selectors = []
                domain = urlparse(link).netloc
                if 'sciencedaily.com' in domain:
                    selectors = ['article', '.content', '.story', '.post-content']
                elif 'webmd.com' in domain:
                    selectors = ['.article-content', '.post-content', 'article', '.content']
                elif 'reuters.com' in domain:
                    selectors = ['[data-testid="BodyWrapper"]', '.resizeableText', '.StandardArticleBody_body']
                elif 'medicalnewstoday.com' in domain:
                    selectors = ['.content', '.article-body', 'article']
                elif 'healthline.com' in domain:
                    selectors = ['.content', '.article-body', '.structured-content', 'article']
                elif 'mindbodygreen.com' in domain:
                    selectors = ['.content', '.article-body', '.post-content', 'article']
                elif 'hsph.harvard.edu' in domain:
                    selectors = ['.post-content', '.content', 'article', '.entry-content']
                # ... добавьте селекторы для других источников ...

                if selectors:
                    time.sleep(1) # Пауза между запросами
                    extracted_data = extract_content_from_page(link, selectors)
                    if extracted_data['content']:
                        content = extracted_data['content']
                        image_url = extracted_data['image_url'] # Получаем изображение из функции
                        logger.info(f"Полный контент и изображение извлечены для статьи: {title} ({link})")
                    else:
                        logger.warning(f"Полный контент НЕ извлечён для статьи: {title} ({link}), используем description.")
                else:
                    logger.info(f"Нет известных селекторов для {domain}, используем description.")

            # --- /НОВАЯ ЛОГИКА ---

            # Формируем словарь для статьи
            article_data = {
                'title': title,
                'link': link,
                'description': description,
                'content': content,
                'image_url': image_url, # Передаём изображение
                'published_at': published_at,
            }
            articles.append(article_data)

        logger.info(f"Найдено {len(articles)} статей в ленте {feed_url}")
        return articles

    except Exception as e:
        logger.error(f"Ошибка при парсинге RSS-ленты {feed_url}: {e}")
        return []
