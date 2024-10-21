from django.core.mail import send_mail
from django.utils import timezone
from notification_app.models import Notification, SendMailTo, SendLog, Status


def send_mails(notification: Notification):
    mail_item = notification.mail
    subject = mail_item.title
    message = mail_item.content

    if notification.status.pk == 3:
        return  # Завершаем функцию, если статус неактивный
    elif notification.status.pk == 1:
        notification.status = Status.objects.get(pk=2)
        notification.save()

    recipient_emails = list(SendMailTo.objects.filter(notification=notification.pk).values_list('client__email', flat=True))

    if recipient_emails:
        is_success = False
        server_response = ""

        try:
            send_mail(
                subject,
                message,
                None,  # Отправитель не указывается, используется DEFAULT_FROM_EMAIL
                recipient_emails,
                fail_silently=False,
            )
            is_success = True
            server_response = "Mail sent successfully to all recipients"
        except Exception as e:
            server_response = str(e)

        SendLog.objects.create(
            notification=notification,
            date_time=timezone.now(),
            is_success=is_success,
            answer=server_response,
        )
