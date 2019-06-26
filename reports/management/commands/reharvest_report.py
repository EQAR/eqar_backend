from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from reports.models import Report
from submissionapi.tasks import download_file


class Command(BaseCommand):
    help = 'Reharvest files for report.'

    def add_arguments(self, parser):
        parser.add_argument('--report', dest='report_id', help='The report ID of the Report.')

    def handle(self, *args, **options):
        if not options['report_id']:
            raise CommandError('--report parameter should be set.')

        try:
            report_id = int(options['report_id'])
            report = Report.objects.get(id=report_id)
        except ObjectDoesNotExist:
            raise CommandError('Report ID "%s" does not exist' % report_id)

        for rf in report.reportfile_set.all():
            download_file.delay(rf.file_original_location, rf.id, report.agency.acronym_primary)

