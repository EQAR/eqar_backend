import os

import filetype
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from agencies.models import Agency
from reports.models import Report
from submissionapi.tasks import download_file


class Command(BaseCommand):
    help = 'Reharvest files for report.'
    force = False

    def add_arguments(self, parser):
        parser.add_argument('--report', dest='report_id',
                            help='The report ID of the Report.', default=0)
        parser.add_argument('--agency', dest='agency',
                            help='The acronym of the agency.', default=None)
        parser.add_argument('--force', dest='force',
                            help='Force reharvest regardless of existing materials', default=False)

    def handle(self, *args, **options):
        report_id = int(options['report_id'])
        agency = options['agency']

        if report_id == 0 and not agency:
            raise CommandError('Report ID or Agency should be set.')

        self.force = options['force']

        # Harvest report with id
        if report_id != 0:
            try:
                report = Report.objects.get(id=report_id)
            except ObjectDoesNotExist:
                raise CommandError('Report ID "%s" does not exist' % report_id)

            self.harvest_report(report)

        # Harvest reports submitted by agency
        if agency:
            try:
                agency = Agency.objects.get(acronym_primary=agency)
            except ObjectDoesNotExist:
                raise CommandError('Agency "%s" does not exist' % agency)

            reports = Report.objects.filter(agency=agency)

            for report in reports:
                self.harvest_report(report)

    def harvest_report(self, report):
        for rf in report.reportfile_set.all():
            if self.force:
                harvest = True
            else:
                harvest = False

            if rf.file == '':
                if rf.file_original_location == '':
                    harvest = False
                else:
                    harvest = True
            else:
                if os.path.exists(rf.file.path):
                    ft = filetype.guess(rf.file)
                    if ft is None:
                        harvest = True
                    else:
                        if ft.mime != 'application/pdf':
                            harvest = True
                else:
                    harvest = True

            if harvest:
                download_file.delay(rf.file_original_location, rf.id, report.agency.acronym_primary)
