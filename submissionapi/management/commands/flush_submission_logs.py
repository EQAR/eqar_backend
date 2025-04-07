from django.core.management import BaseCommand, CommandError

from django.conf import settings

from datetime import datetime, timedelta

from submissionapi.models import SubmissionPackageLog

class Command(BaseCommand):
    help = 'Flush old submission log entries'

    PAGESIZE = 5000

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show how many log entries would be deleted, but do not actually delete")
        parser.add_argument("--flush-all", "-a", action='store_true',
                            help="Delete the whole log")
        parser.add_argument("--days-ago", "-d", type=int,
                            help="Delete log entries older than the specified number of days")

    def handle(self, *args, dry_run, flush_all, days_ago, **options):
        log_all = SubmissionPackageLog.objects.all()
        if flush_all:
            to_delete = log_all
        elif days_ago:
            delete_before = datetime.now()-timedelta(days=days_ago)
            to_delete = log_all.filter(submission_date__lt=delete_before)
        else:
            raise CommandError('You need to specify either --flush-all or --days-ago')

        self.stdout.write(f'Deleting {to_delete.count()} of {log_all.count()} log entries...')

        if not dry_run:
            self.stdout.write(str(to_delete.delete()))
        else:
            self.stdout.write('--- dry run, nothing deleted ---')

