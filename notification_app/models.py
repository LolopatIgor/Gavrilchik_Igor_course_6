from django.db import models
from users.models import User

NULLABLE = {'blank': True, 'null': True}

class Period(models.Model):
    name = models.CharField(max_length=200, verbose_name='Период')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Период'
        verbose_name_plural = 'Периоды'


class Status(models.Model):
    name = models.CharField(max_length=200, verbose_name='Статус')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

class Mail(models.Model):
    title = models.CharField(max_length=400, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст письма')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец', related_name='mails', **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Письмо'
        verbose_name_plural = 'Письма'


class Notification(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название рассылки')
    scheduled_time = models.DateTimeField(verbose_name='Дата и время первой отправки рассылки')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name='Период', related_name='notifications')
    status = models.ForeignKey(Status, on_delete=models.CASCADE, verbose_name='Статус', related_name='notifications')
    mail = models.ForeignKey(Mail, on_delete=models.CASCADE, verbose_name='Письмо', related_name='mails')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец', related_name='notifications', **NULLABLE)

    def __str__(self):
        return f"{self.name} ({self.period}, {self.status})"

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Client(models.Model):
    surname = models.CharField(max_length=200, verbose_name='Фамилия')
    name = models.CharField(max_length=200, verbose_name='Имя')
    patronymic_name = models.CharField(max_length=200, verbose_name='Отчество')
    email = models.EmailField(max_length=254, unique=True)
    description = models.CharField(max_length=800, verbose_name='Описание')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец', related_name='clients', **NULLABLE)

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic_name}"

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class SendMailTo(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент', related_name='send_mail_to')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, verbose_name='Рассылка', related_name='send_mail_to')

    def __str__(self):
        return f"{self.client} - {self.notification.name}"

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'

class SendLog(models.Model):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, verbose_name='Рассылка', related_name='send_log')
    date_time = models.DateTimeField(verbose_name='Дата и время попытки')
    is_success = models.BooleanField(verbose_name='Успешно')
    answer = models.TextField(verbose_name='Ответ почтового сервера')

    def __str__(self):
        return f"{self.notification} - {self.date_time} - {'Success' if self.is_success else 'Failed'}"
