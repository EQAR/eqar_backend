from django.core.management import BaseCommand

from agencies.indexers.agency_indexer import AgencyIndexer
from agencies.models import Agency


class Command(BaseCommand):
    help = 'Index Agency records.'

    def handle(self, *args, **options):
        for agency in Agency.objects.iterator():
            indexer = AgencyIndexer(agency)
            indexer.index()
