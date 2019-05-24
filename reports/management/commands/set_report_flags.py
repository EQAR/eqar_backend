from django.core.management import BaseCommand

from reports.models import Report, ReportFlag
from submissionapi.tasks import recheck_flag


class Command(BaseCommand):
    help = 'Set Report record dates.'

    def handle(self, *args, **options):
        for report in Report.objects.iterator():
            recheck_flag(report=report)
            print("Updating flags in report %s" % report.id)

        for report_flag in ReportFlag.objects.iterator():
            report_flag.created_at = report_flag.report.created_at
            report_flag.save()
