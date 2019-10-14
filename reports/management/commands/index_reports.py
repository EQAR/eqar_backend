import pysolr
from django.core.management import BaseCommand
from django.conf import settings

from reports.indexers.reports_indexer import ReportsIndexer
from reports.models import Report


class Command(BaseCommand):
    help = 'Index Report records.'

    def handle(self, *args, **options):
        solr_core = getattr(settings, "SOLR_CORE_REPORTS", "deqar-reports")
        solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        solr = pysolr.Solr(solr_url)
        solr.delete(q='*:*', commit=True)

        for report in Report.objects.iterator():
            indexer = ReportsIndexer(report)
            indexer.index()
