#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from users.utils import UsersUtils

def send_weekly_email():
    UsersUtils.send_weekly_email()

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splitwise_project.settings')
    try:
        from django.core.management import execute_from_command_line

        # Scheduling the email for every week
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_weekly_email, 'interval', weeks=1)
        scheduler.start()

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
