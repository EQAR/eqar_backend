import argparse
import csv
import json
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.conf import settings

from django.test.client import RequestFactory

from reports.models import Report
from webapi.serializers.report_detail_serializers import ReportDetailSerializer
from rest_framework.renderers import JSONRenderer

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

    def handle(self, LIST, check, backup, *args, **options):

        base_dir = os.path.join(settings.MEDIA_ROOT, backup)
        os.makedirs(base_dir, exist_ok=True)

        request_factory = RequestFactory()
        settings.ALLOWED_HOSTS.append('testserver')
        renderer = JSONRenderer()

        reader = csv.DictReader(LIST)
        for row in reader:
            try:
                report = Report.objects.get(id=row['report_id'])
            except ObjectDoesNotExist:
                self.stdout.write(self.style.WARNING(f"Report with ID {row['report_id']} does not exist."))
                continue
            except KeyError:
                self.stdout.write(self.style.WARNING(f"You must specify the report ID in a column name 'report_id'."))
                continue

            if check and report.agency.acronym_primary != row['agency']:
                self.stdout.write(self.style.ERROR(f"Agency mismatch: CSV={row['agency']} DEQAR={report.agency.acronym_primary}"))
                continue

            self.stdout.write(f"Deleting report {report.id} by {report.agency.acronym_primary}")
            with open(os.path.join(base_dir, f'{report.id}.json'), 'wb') as bkupfile:
                bkupfile.write(renderer.render(ReportDetailSerializer(report, context={'request': request_factory.get(f'/webapi/v2/browse/reports/{report.id}/')}).data))
            report.delete()

