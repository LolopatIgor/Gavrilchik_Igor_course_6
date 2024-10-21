import json
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Loads permissions and groups from a JSON dump'

    def handle(self, *args, **options):
        # Путь к вашему JSON файлу
        json_file_path = 'manager_dump.json'

        try:
            # Загружаем данные из JSON файла
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                # Используем команду loaddata для импорта данных
                call_command('loaddata', json_file_path)
                self.stdout.write(self.style.SUCCESS('Successfully loaded permissions and groups.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
