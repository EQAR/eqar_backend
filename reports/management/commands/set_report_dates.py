from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from reports.models import Report
from submissionapi.models import SubmissionReportLog


class Command(BaseCommand):
    help = 'Set Report record dates.'

    def handle(self, *args, **options):
        for report in Report.objects.iterator():
            try:
                sp_log_early = SubmissionReportLog.objects.filter(report=report).earliest('submission_date')
                sp_log_latest = SubmissionReportLog.objects.filter(report=report).latest('submission_date')

                report.created_at = sp_log_early.submission_date
                report.created_by = sp_log_early.submission_package_log.user.user
                report.updated_at = sp_log_latest.submission_date
                report.updated_by = sp_log_latest.submission_package_log.user.user

            except ObjectDoesNotExist:
                agency = report.agency.acronym_primary.lower()
                user = User.objects.get(username=agency)
                report.created_by = user
                report.updated_by = user
            report.save()
            print("Updating report %s" % report.id)