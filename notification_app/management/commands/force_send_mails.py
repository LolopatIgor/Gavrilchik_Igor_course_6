from gi.types import nothing

from notification_app.models import Notification
from notification_app.services import send_mails
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        for item in Notification.objects.filter():
            print(f"{item.pk} - {item.name}")

        input_id = ""
        cur_notification = None
        while input_id == "":
            try:
                input_id = input("Выберите рассылку для отправки: \n")
                cur_notification = Notification.objects.get(pk=input_id)
            except Notification.DoesNotExist:
                print(f"Рассылка с ID {input_id} не найдена. Пожалуйста, попробуйте снова.")
            except ValueError:
                print("Пожалуйста, введите корректное числовое значение для ID.")

        send_mails(cur_notification)