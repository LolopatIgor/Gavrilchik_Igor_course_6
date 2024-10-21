from django.core.management.base import BaseCommand
from django_apscheduler.models import DjangoJob
from datetime import datetime

class Command(BaseCommand):
    help = 'Show all scheduled jobs'

    def handle(self, *args, **options):
        current_time = datetime.now()
        print("Текущее время:", current_time)
        jobs = DjangoJob.objects.all()
        if jobs.exists():
            for job in jobs:
                self.stdout.write(f"Job ID: {job.id}, Next Run Time: {job.next_run_time}, Job State: {job.job_state}")
        else:
            self.stdout.write("No scheduled jobs found.")