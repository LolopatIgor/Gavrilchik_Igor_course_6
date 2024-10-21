from django.db import models
from django.utils.text import slugify

NULLABLE = {'blank': True, 'null': True}


class Blog(models.Model):
    title = models.CharField(max_length=400, verbose_name='Заголовок')
    slug = models.CharField(max_length=100, verbose_name='slug')
    body = models.TextField(verbose_name='Содержимое')
    image = models.ImageField(upload_to='blog/', verbose_name='Превью', **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_published = models.BooleanField(default=False, verbose_name='Признак публикации')
    view_count = models.DecimalField(default=0, max_digits=10, decimal_places=0, verbose_name='Счётчик просмотров')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блоги'

