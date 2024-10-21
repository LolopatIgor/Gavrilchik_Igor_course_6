import json
from django.core.management.base import BaseCommand
from notification_app.models import Period, Status, Mail

class Command(BaseCommand):
    help = 'Fill the database with initial data from notification_app_data.json'

    def handle(self, *args, **options):
        # Открываем файл и загружаем данные
        with open('notification_app_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проходим по данным и сохраняем их в соответствующие модели
        for entry in data:
            model = entry['model']
            pk = entry['pk']
            fields = entry['fields']

            if model == 'notification_app.period':
                Period.objects.update_or_create(defaults=fields, pk=pk)
            elif model == 'notification_app.status':
                Status.objects.update_or_create(defaults=fields, pk=pk)
            elif model == 'notification_app.mail':
                Mail.objects.update_or_create(defaults=fields, pk=pk)

        self.stdout.write(self.style.SUCCESS('Database filled successfully.'))
