import pysolr
from django.core.management import BaseCommand
from django.conf import settings

from agencies.indexers.agency_indexer import AgencyIndexer
from agencies.models import Agency


class Command(BaseCommand):
    help = 'Index Agency records.'

    def handle(self, *args, **options):
        solr_core = getattr(settings, "SOLR_CORE_AGENCIES", "deqar-agencies")
        solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        solr = pysolr.Solr(solr_url)
        solr.delete(q='*:*', commit=True)

        for agency in Agency.objects.iterator():
            indexer = AgencyIndexer(agency)
            indexer.index()
