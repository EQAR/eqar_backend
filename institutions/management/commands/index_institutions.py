import pysolr
from django.core.management import BaseCommand
from django.conf import settings

from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.models import Institution


class Command(BaseCommand):
    help = 'Index Institution records.'

    def handle(self, *args, **options):
        solr_core = getattr(settings, "SOLR_CORE_INSTITUTIONS", "deqar-institutions")
        solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        solr = pysolr.Solr(solr_url)
        solr.delete(q='*:*', commit=True)

        for inst in Institution.objects.iterator():
            indexer = InstitutionIndexer(inst.id)
            indexer.index()
