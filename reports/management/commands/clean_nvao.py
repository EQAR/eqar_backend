from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from agencies.models import Agency
from submissionapi.models import SubmissionReportLog


class Command(BaseCommand):
    help = 'Clean reports submitted in 2018 by NVAO.'

    def handle(self, *args, **options):
        agency = Agency.objects.get(acronym_primary='NVAO')
        logs = SubmissionReportLog.objects.filter(
            agency=agency,
            submission_date__year=2018
        )

        for log in logs:
            print("Deleting report no. %s" % log.report_id)
            try:
                log.report.delete()
            except ObjectDoesNotExist:
                print("Report no. %s was already removed!" % log.report_id)