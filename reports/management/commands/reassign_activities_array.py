import hashlib
import os

from django.core.management import BaseCommand, CommandError
from django.conf import settings
from reports.models import Report

class Command(BaseCommand):
    help = 'Create checksum for the existing files and save it to the DB.'
    force = False

    def add_arguments(self, parser):
        parser.add_argument('--report',
                            help='The report ID of the Report.', type=int)

    def handle(self, *args, report=None, **options):
        # Harvest report with id
        if report:
            reports = Report.objects.filter(id=report)
            if reports.count() == 0:
                raise CommandError('Report ID "%s" does not exist' % report)
        else:
            reports = Report.objects.all()

        for report in reports.all():
            print("Processing report: ", report.id)
            report.agency_esg_activities.clear()
            report.agency_esg_activities.add(report.agency_esg_activity)
            report.save()