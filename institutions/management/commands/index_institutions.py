from django.core.management import BaseCommand

from institutions.indexers.institution_indexer import InstitutionIndexer
from institutions.models import Institution


class Command(BaseCommand):
    help = 'Index Institution records.'

    def handle(self, *args, **options):
        for inst in Institution.objects.iterator():
            indexer = InstitutionIndexer(inst)
            indexer.index()
