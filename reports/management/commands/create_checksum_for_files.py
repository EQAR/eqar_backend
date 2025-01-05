import hashlib
import os
import time

import filetype
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from djoser.conf import settings

from agencies.models import Agency
from reports.models import Report
from submissionapi.tasks import download_file

from requests.exceptions import RequestException

class Command(BaseCommand):
    help = 'Reharvest files for report.'
    force = False

    def add_arguments(self, parser):
        parser.add_argument('--report',
                            help='The report ID of the Report.', type=int)

    def handle(self, *args, report=None, all=False, **options):
        # Harvest report with id
        if report:
            reports = Report.objects.filter(id=report)
            if reports.count() == 0:
                raise CommandError('Report ID "%s" does not exist' % report)
        else:
            reports = Report.objects.all()

        for report in reports.all():
            for report_file in report.reportfile_set.all():
                if report_file.file_checksum is None or report_file.file_checksum == '':
                    file_path = os.path.join(
                        settings.MEDIA_ROOT,
                        report.agency_acronym,
                        report_file.local_filename
                    )

                    # Check if the downloaded file is different from the old file
                    with open(file_path, 'rb') as f:
                        checksum = hashlib.md5(f.read()).hexdigest()

                    report_file.file_checksum = checksum
                    report_file.save()
                    print(f"Updated checksum for {report_file.local_filename} to {checksum}")