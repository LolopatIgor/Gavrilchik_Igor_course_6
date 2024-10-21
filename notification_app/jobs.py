from apscheduler.triggers.interval import IntervalTrigger
from .models import Notification
from apscheduler.jobstores.base import JobLookupError
from .services import send_mails
from datetime import datetime
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from django.utils.timezone import now
from datetime import timedelta

scheduler = BackgroundScheduler()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        # Проходим по всем задачам
        jobs = DjangoJob.objects.all()
        for job in jobs:
            try:
                notification = Notification.objects.get(pk=job.id)  # Получаем соответствующую запись из Notification
                interval = get_interval_from_notification(notification)  # Получаем интервал на основе поля period

                # Рассчитываем next_run_time
                next_run_time = job.next_run_time
                send_mail_flag = False  # Флаг, чтобы выполнить рассылку только один раз

                # Пока next_run_time в прошлом, продолжаем его сдвигать
                while next_run_time < now():
                    next_run_time += interval
                    send_mail_flag = True  # Отметим, что рассылка должна быть выполнена

                # Если произошёл сдвиг и рассылка нужна, выполняем её немедленно
                if send_mail_flag:
                    send_mails(notification)  # Немедленный запуск

                # Добавляем задачу в планировщик
                scheduler.add_job(
                    execute_job,  # Ваша функция
                    trigger=IntervalTrigger(seconds=interval.total_seconds()),  # Интервал
                    args=[job.id],  # Передаем ID задачи
                    id=str(job.id),  # Уникальный ID
                    replace_existing=True,  # Заменить, если задача уже существует
                    next_run_time=next_run_time  # Устанавливаем следующее время запуска
                )

            except Notification.DoesNotExist:
                print(f"Notification with ID {job.id} does not exist. Skipping job.")
                remove_job(job.id)

        scheduler.start()

def get_interval_from_notification(notification):
    """Возвращаем интервал для планировщика на основе поля period."""
    if notification.period == 1:  # Раз в день
        return timedelta(days=1)
    elif notification.period == 2:  # Раз в неделю
        return timedelta(weeks=1)
    elif notification.period == 3:  # Раз в месяц (30 дней)
        return timedelta(days=30)
    else:
        return timedelta(days=1)  # Значение по умолчанию

def execute_job(job_id):
    print(f"Executing job {job_id} at {datetime.now()}")
    try:
        notification = Notification.objects.get(pk=job_id)
        send_mails(notification)  # вызываем вашу функцию отправки почты
    except Notification.DoesNotExist:
        print(f"Notification with ID {job_id} does not exist. Removing job.")
        remove_job(job_id)
    except Exception as e:
        print(f"An error occurred: {e}")

def schedule_job(notification: Notification):
    if notification.period.pk == 1:
        trigger = IntervalTrigger(days=1)
    elif notification.period.pk == 2:
        trigger = IntervalTrigger(weeks=1)
    elif notification.period.pk == 3:
        trigger = IntervalTrigger(days=30)
    else:
        raise ValueError("Неверный интервал. Используйте 1 (день), 2 (неделя) или 3 (месяц).")

    interval = get_interval_from_notification(notification)  # Получаем интервал на основе поля period

    # Рассчитываем next_run_time
    next_run_time = notification.scheduled_time


    # Пока next_run_time в прошлом, продолжаем его сдвигать
    while next_run_time < now():
        next_run_time += interval


    print(notification.scheduled_time)
    scheduler.add_job(execute_job, trigger, id=str(notification.pk),
                      replace_existing=True, args=[notification.pk],
                      next_run_time=next_run_time)  # Используйте next_run_time


def remove_job(notification_pk):
    try:
        # Удаляем связанные записи выполнения из базы данных
        DjangoJobExecution.objects.filter(job_id=str(notification_pk)).delete()
        print(f"All executions for job ID {notification_pk} have been removed from the database.")

        # Удаляем саму задачу из базы данных
        DjangoJob.objects.filter(id=str(notification_pk)).delete()
        print(f"Job with ID {notification_pk} has been removed from the database.")

        # Удаляем задачу из планировщика
        scheduler.remove_job(str(notification_pk))
        print(f"Job with ID {notification_pk} has been removed from scheduler.")
    except JobLookupError:
        print(f"Job with ID {notification_pk} not found in scheduler.")