import sys
from django.apps import AppConfig

class NotificationAppConfig(AppConfig):
    name = 'notification_app'

    def ready(self):
        # Проверяем, не запускаются ли миграции
        if 'runserver' in sys.argv or 'uwsgi' in sys.argv:
            from notification_app.jobs import start_scheduler
            start_scheduler()
