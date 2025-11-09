import hashlib
import os

from django.core.management import BaseCommand, CommandError
from django.conf import settings
from reports.models import Report

class Command(BaseCommand):
    help = 'Create checksum for the existing files and save it to the DB.'
    force = False

    def add_arguments(self, parser):
        parser.add_argument('--all',
                            action='store_true',
                            help='Calculate checksums for all reports.')
        parser.add_argument('--report',
                            help='Calculate checksum for a specific report', type=int)
        parser.add_argument('--check', '-c',
                            action='store_true',
                            help='Verify checksums already saved in database.')
        parser.add_argument('--force', '-f',
                            action='store_true',
                            help='Overwrite checksums saved in database in case of mismatch.')

    def handle(self, *args, report=None, all=False, check=False, force=False, verbosity=1, **options):
        # Calculate checksum of a single report
        if report:
            reports = Report.objects.filter(id=report)
            if reports.count() == 0:
                raise CommandError('Report ID "%s" does not exist' % report)
        # Calculate checksums for all reports
        elif all:
            reports = Report.objects.all()
        else:
            raise CommandError('Specify either Report ID or --all.')

        stats = {
            'total': reports.count(),
            'checked': 0,
            'missing': 0,
            'done': 0,
            'mismatch': 0,
        }

        for report in reports.exclude(reportfile__file='').distinct().iterator():
            for report_file in report.reportfile_set.exclude(file=''):
                if check or report_file.file_checksum is None or report_file.file_checksum == '':
                    stats['checked'] += 1
                    try:
                        checksum = report_file.generate_checksum()

                    except FileNotFoundError:
                        stats['missing'] += 1
                        if verbosity > 1:
                            if report_file.file.name:
                                self.stderr.write(self.style.WARNING(f"File {report_file.file.name} could not be found"))
                            else:
                                self.stderr.write(self.style.WARNING(f"ReportFile {report_file.id} ({report_file.file_display_name} from {report_file.file_original_location}) has no local file path"))

                    else:
                        stats['done'] += 1
                        if check and report_file.file_checksum:
                            if report_file.file_checksum == checksum:
                                self.stdout.write(self.style.SUCCESS(f"Correct checksum in database for {report_file.file.name}"))
                            else:
                                stats['mismatch'] += 1
                                self.stdout.write(self.style.ERROR(f"Checksum mismatch for {report_file.file.name}: database={report_file.file_checksum} file={checksum}"))
                                if force:
                                    report_file.file_checksum = checksum
                                    report_file.save()
                                    self.stdout.write(self.style.WARNING(f" -> value in database overwritten by {checksum}"))
                        else:
                            report_file.file_checksum = checksum
                            report_file.save()
                            self.stdout.write(self.style.SUCCESS(f"Calculated checksum for {report_file.file.name} to {checksum}"))

        self.stdout.write("""
            {total} reports checked
            {checked} file checksums were missing
            {missing} files were not found
            {done} checksums were calculated
            {mismatch} mismatches identified
        """.format(**stats))

