from django.core.management import BaseCommand

from reports.indexers.reports_indexer import ReportsIndexer
from reports.models import Report
from reports.indexers.reports_all_indexer import ReportsAllIndexer


class Command(BaseCommand):
    help = 'Index Report records.'

    def handle(self, *args, **options):
        for report in Report.objects.iterator():
            indexer = ReportsIndexer(report)
            indexer.index()
