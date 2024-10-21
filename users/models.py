from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE_OPTIONS = {'blank': True, 'null': True}

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='почта')

    first_name = models.CharField(max_length=30, blank=True, verbose_name='Имя')
    last_name = models.CharField(max_length=30, blank=True, verbose_name='Фамилия')

    phone = models.CharField(max_length=35, verbose_name='телефон', **NULLABLE_OPTIONS)
    avatar = models.ImageField(upload_to='users/', verbose_name='аватар', **NULLABLE_OPTIONS)
    country = models.CharField(max_length=50, verbose_name='страна', **NULLABLE_OPTIONS)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            # Добавьте необходимые разрешения здесь
        ]