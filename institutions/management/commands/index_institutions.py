from django.core.management import BaseCommand

from institutions.indexers.institution_report_indexer import InstitutionReportIndexer
from institutions.models import Institution


class Command(BaseCommand):
    help = 'Index Institution records.'

    def handle(self, *args, **options):
        for inst in Institution.objects.iterator():
            indexer = InstitutionReportIndexer(inst)
            indexer.index()
