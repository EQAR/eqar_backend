from django.core.management import BaseCommand

from reports.models import Report
from reports.indexers.reports_all_indexer import ReportsAllIndexer


class Command(BaseCommand):
    help = 'Index Report records.'

    def handle(self, *args, **options):
        for report in Report.objects.iterator():
            indexer = ReportsAllIndexer(report)
            indexer.index()
