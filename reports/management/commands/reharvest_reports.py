import os
import time

import filetype
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from agencies.models import Agency
from reports.models import Report
from submissionapi.tasks import download_file

from requests.exceptions import RequestException

class Command(BaseCommand):
    help = 'Reharvest files for report.'
    force = False

    def add_arguments(self, parser):
        parser.add_argument('--all', '-a',
                            help='Check all Reports in the database.', action='store_true')
        parser.add_argument('--report',
                            help='The report ID of the Report.', type=int)
        parser.add_argument('--agency',
                            help='The acronym of the agency.')
        parser.add_argument('--force', '-f',
                            help='Force reharvest regardless of existing materials', action='store_true')
        parser.add_argument('--check-type', '-t',
                            help='Reharvest existing files that do not seem to be a PDF.', action='store_true')
        parser.add_argument('--dry-run', '-n',
                            help='Only log which files would be reharvested.', action='store_true')
        parser.add_argument('--sync', '-s',
                            help='Download files synchronously.', action='store_true')
        parser.add_argument('--delay', '-d',
                            help='In synchronous mode, wait N seconds between downloads.', type=float)

    def handle(self, *args, report=None, agency=None, all=False, dry_run=False, force=False, check_type=False, sync=False, delay=None, verbosity, **options):
        self.force = force
        self.dry_run = dry_run
        self.check_type = check_type
        self.sync = sync
        self.delay = delay
        self.verbosity = verbosity

        # Counters for stats
        self.count_missing = 0
        self.count_nosource = 0
        self.count_wrongtype = 0
        self.count_force = 0
        self.count_success = 0
        self.count_failed = 0

        # Harvest report with id
        if report:
            reports = Report.objects.filter(id=report)
            if reports.count() == 0:
                raise CommandError('Report ID "%s" does not exist' % report)

        # Harvest reports submitted by agency
        elif agency:
            try:
                agency = Agency.objects.get(acronym_primary=agency)
            except ObjectDoesNotExist:
                raise CommandError('Agency "%s" does not exist' % agency)

            reports = Report.objects.filter(agency=agency)

        # Harvest all reports
        elif all:
            reports = Report.objects.all()

        else:
            raise CommandError('Specify Agency, Report ID or --all.')

        # Run harvest
        try:
            for report in reports.iterator():
                self.harvest_report(report)
        except KeyboardInterrupt:
            pass

        # Print stats
        self.stdout.write(f'\nMissing: {self.count_missing}\nMissing, but not URL: {self.count_nosource}\nWrong type: {self.count_wrongtype}\nReharvest forced: {self.count_force}')
        if self.sync and not self.dry_run:
            self.stdout.write(f'\nSuccess: {self.count_success}\nFailed: {self.count_failed}')


    def harvest_report(self, report):
        for rf in report.reportfile_set.all():
            harvest = False

            if rf.file == '':
                if rf.file_original_location == '':
                    self.stdout.write(self.style.WARNING(f'Report {report.id}, file {rf.id} is missing, but has no source URL'))
                    self.count_nosource += 1
                else:
                    self.stdout.write(self.style.WARNING(f'Report {report.id}, file {rf.id} is missing'))
                    harvest = True
                    self.count_missing += 1
            else:
                if os.path.exists(rf.file.path):
                    if self.force:
                        harvest = True
                        self.stdout.write(self.style.WARNING(f'Report {report.id}, file {rf.id} at {rf.file.path} will be reharvested because --force/-f is set'))
                        self.count_force += 1
                    elif self.check_type:
                        ft = filetype.guess(rf.file)
                        if ft is None:
                            self.stdout.write(self.style.WARNING(f'Report {report.id}, file {rf.id} at {rf.file.path} has unknown type'))
                            harvest = True
                            self.count_wrongtype += 1
                        else:
                            if ft.mime == 'application/pdf':
                                if self.verbosity > 1:
                                    self.stdout.write(f'Report {report.id}, file {rf.id} at {rf.file.path} is a PDF')
                            else:
                                self.stdout.write(self.style.WARNING(f'Report {report.id}, file {rf.id} at {rf.file.path} is of type {ft.mime} instead of PDF'))
                                harvest = True
                                self.count_wrongtype += 1
                    elif self.verbosity > 1:
                        self.stdout.write(f'Report {report.id}, file {rf.id} at {rf.file.path} exists')
                else:
                    if rf.file_original_location == '':
                        self.stdout.write(self.style.WARNING(f'Report {report.id}, file {rf.id} is missing but has no source URL'))
                        self.count_nosource += 1
                    else:
                        self.stdout.write(self.style.WARNING(f'Report {report.id}, file {rf.id} should be at {rf.file.path} but is missing'))
                        harvest = True
                        self.count_missing += 1

            if harvest:
                self.stdout.write(f'-> download from {rf.file_original_location}')
                if not self.dry_run:
                    if self.sync:
                        if self.delay:
                            time.sleep(self.delay)
                        try:
                            download_file(rf.file_original_location, rf.id, report.agency.acronym_primary)
                        except RequestException as e:
                            self.stdout.write(self.style.ERROR(f'-> failed, Exception: {e}'))
                            self.count_failed += 1
                        else:
                            rf.refresh_from_db()
                            if rf.file != '' and os.path.exists(rf.file.path):
                                self.stdout.write(self.style.SUCCESS(f'-> saved as {rf.file.path}'))
                                self.count_success += 1
                            else:
                                self.stdout.write(self.style.ERROR(f'-> failed, possibly wrong content-type or 404 error.'))
                                self.count_failed += 1
                    else:
                        download_file.delay(rf.file_original_location, rf.id, report.agency.acronym_primary)

