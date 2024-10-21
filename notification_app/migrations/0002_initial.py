# Generated by Django 5.1.2 on 2024-10-21 21:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('notification_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='mail',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mails', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='notification',
            name='mail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mails', to='notification_app.mail', verbose_name='Письмо'),
        ),
        migrations.AddField(
            model_name='notification',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='Владелец'),
        ),
        migrations.AddField(
            model_name='notification',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='notification_app.period', verbose_name='Период'),
        ),
        migrations.AddField(
            model_name='sendlog',
            name='notification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_log', to='notification_app.notification', verbose_name='Рассылка'),
        ),
        migrations.AddField(
            model_name='sendmailto',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_mail_to', to='notification_app.client', verbose_name='Клиент'),
        ),
        migrations.AddField(
            model_name='sendmailto',
            name='notification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_mail_to', to='notification_app.notification', verbose_name='Рассылка'),
        ),
        migrations.AddField(
            model_name='notification',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='notification_app.status', verbose_name='Статус'),
        ),
    ]