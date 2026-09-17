from django.conf import settings
from django.db import models

from pytils.translit import slugify

from .constants import MAX_SLUG_LENGTH, MAX_TITLE_LENGTH


class Note(models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=MAX_TITLE_LENGTH,
        default='Название заметки',
        help_text='Дайте короткое название заметке'
    )
    text = models.TextField(
        'Текст',
        help_text='Добавьте подробностей'
    )
    slug = models.SlugField(
        'Адрес для страницы с заметкой',
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        blank=True,
        help_text=('Укажите адрес для страницы заметки. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:MAX_SLUG_LENGTH]
        super().save(*args, **kwargs)
