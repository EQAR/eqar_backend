import argparse
import csv
import json
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.conf import settings

from reports.models import Report
from webapi.v2.serializers.report_detail_serializers import ReportDetailSerializer
from rest_framework.renderers import JSONRenderer

from urllib.parse import urljoin

class FakeRequest:
    """
    This class allows the serializer to create URIs correctly.
    """

    GET = {}

    def __init__(self, root):
        self.root = root

    def build_absolute_uri(self, rel_uri):
        return urljoin(self.root, rel_uri)


class Command(BaseCommand):
    help = 'Delete Report records and save a copy'

    def add_arguments(self, parser):
        parser.add_argument('LIST',
                            type=argparse.FileType('r'),
                            help='List of reports to be deleted.')
        parser.add_argument('--check', '-c',
                            action='store_true',
                            help='Check whether reports belong to specified agency.')
        parser.add_argument('--backup', '-b',
                            default='deleted-reports',
                            help='The directory (relative to MEDIA_ROOT) where to place exported files.')
        parser.add_argument('--dry-run', '-n',
                            action='store_true',
                            help='Dry-run: only save backup files but do not delete from database.')
        parser.add_argument('--root', '-r',
                            default='/',
                            help='The root URL to prefix links to report files with.')

    def handle(self, LIST, check, backup, root, dry_run, *args, **options):

        base_dir = os.path.join(settings.MEDIA_ROOT, backup)
        os.makedirs(base_dir, exist_ok=True)

        request = FakeRequest(root)
        renderer = JSONRenderer()

        reader = csv.DictReader(LIST)
        for row in reader:
            if 'report_id' in row:
                try:
                    report = Report.objects.get(id=row['report_id'])
                except ObjectDoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Report with ID {row['report_id']} does not exist."))
                    continue
            elif 'agency' in row and 'local_identifier' in row:
                try:
                    report = Report.objects.get(agency__acronym_primary=row['agency'], local_identifier=row['local_identifier'])
                except ObjectDoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Report with Local ID {row['local_identifier']} ({row['agency']}) does not exist."))
                    continue
            else:
                self.stdout.write(self.style.WARNING(f"You must specify the report ID in a column name 'report_id', or a combination of 'agency' and 'local_identifier'."))
                continue

            if check and report.agency.acronym_primary != row['agency']:
                self.stdout.write(self.style.ERROR(f"Agency mismatch: CSV={row['agency']} DEQAR={report.agency.acronym_primary}"))
                continue

            self.stdout.write(f"Deleting report {report.id} by {report.agency.acronym_primary}")
            with open(os.path.join(base_dir, f'{report.id}.json'), 'wb') as bkupfile:
                bkupfile.write(renderer.render(ReportDetailSerializer(report, context={'request': request}).data))
            if not dry_run:
                report.delete()

