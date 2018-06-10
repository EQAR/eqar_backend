from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from agencies.models import Agency
from reports.models import Report
from submissionapi.downloaders.report_downloader import ReportDownloader
from submissionapi.tasks import download_file


class Command(BaseCommand):
    help = 'Reharvest files for report.'

    def add_arguments(self, parser):
        parser.add_argument('--report', dest='report_id', help='The report ID of the Report.')

    def handle(self, *args, **options):
        if not options['report_id']:
            raise CommandError('--report parameter should be set.')

        try:
            report = Report.objects.get(id=options['report_id'])
        except ObjectDoesNotExist:
            raise CommandError('Report ID "%s" does not exist' % options['report'])

        for rf in report.reportfile_set.all():
            download_file.delay(rf.file_original_location, rf.id, agency.acronym_primary)

