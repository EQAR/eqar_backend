from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from agencies.models import Agency
from reports.models import Report
from submissionapi.tasks import download_file


class Command(BaseCommand):
    help = 'Reharvest files from agency.'

    def add_arguments(self, parser):
        parser.add_argument('--agency', dest='agency_acronym', help='The acronym of the Agency.')

    def handle(self, *args, **options):
        if not options['agency_acronym']:
            raise CommandError('--agency parameter should be set.')

        try:
            agency = Agency.objects.get(acronym_primary=options['agency_acronym'])
        except ObjectDoesNotExist:
            raise CommandError('Agency "%s" does not exist' % options['agency_acronym'])

        reports = Report.objects.filter(agency=agency)

        for report in reports:
            for rf in report.reportfile_set.all():
                download_file.delay(rf.file_original_location, rf.id, agency.acronym_primary)
