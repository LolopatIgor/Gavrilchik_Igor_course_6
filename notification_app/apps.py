from django.apps import AppConfig

class NotificationAppConfig(AppConfig):
    name = 'notification_app'

    def ready(self):
        from notification_app.jobs import start_scheduler
        start_scheduler()
