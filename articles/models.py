# articles/models.py
from django.db import models

CATEGORIES = [
    ('medicine', 'Medicine'),
    ('fitness', 'Fitness'),
    ('nutrition', 'Nutrition'),
    ('lifestyle', 'Lifestyle'),
]

class Article(models.Model):
    title = models.CharField(max_length=500)
    original_content = models.TextField()  # Оригинальный текст из RSS
    processed_content = models.TextField(blank=True)  # Обработанный ИИ
    summary = models.TextField(blank=True)  # Краткое содержание
    source_url = models.URLField(blank=True)  # Ссылка на ОРИГИНАЛЬНУЮ статью (уже было)
    published_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    is_published = models.BooleanField(default=True) # Для публикации/снятия с публикации
    slug = models.SlugField(unique=True, blank=True) # Для URL
    image_url = models.URLField(blank=True, null=True) # Ссылка на изображение статьи
    # --- ОБНОВЛЁННЫЕ/НОВЫЕ ПОЛЯ ---
    # author = models.CharField(max_length=200, blank=True, null=True) # <-- УДАЛЯЕМ ЭТО ПОЛЕ
    source_name = models.CharField(max_length=200, blank=True, null=True) # Название источника (например, "Medical News Today")
    tags = models.CharField(max_length=500, blank=True, null=True) # Теги (можно сделать отдельную модель, но для простоты строка)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            import re
            self.slug = re.sub(r'[^a-zA-Z0-9]', '-', self.title.lower())
        super().save(*args, **kwargs)
