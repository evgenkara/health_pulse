# articles/views.py
from django.shortcuts import render, get_object_or_404
from .models import Article, CATEGORIES # Импортируем CATEGORIES

def article_list(request):
    category = request.GET.get('category')
    if category:
        # Получаем список допустимых категорий из импортированной переменной CATEGORIES
        valid_categories = [choice[0] for choice in CATEGORIES] # Используем CATEGORIES, а не Article.CATEGORIES
        if category in valid_categories:
            articles = Article.objects.filter(is_published=True, category=category).order_by('-published_at')
        else:
            articles = Article.objects.none()
    else:
        articles = Article.objects.filter(is_published=True).order_by('-published_at')

    # Получаем топ-5 статей (например, по дате публикации)
    top_articles = Article.objects.filter(is_published=True).order_by('-published_at')[:5]

    return render(request, 'articles/list.html', {'articles': articles, 'top_articles': top_articles})

def article_detail(request, slug):
    # Используем get_object_or_404 для лучшей обработки ошибок
    article = get_object_or_404(Article, slug=slug)
    # Разбиваем теги в представлении
    tags_list = [tag.strip() for tag in article.tags.split(',')] if article.tags else []
    return render(request, 'articles/detail.html', {'article': article, 'tags_list': tags_list})
