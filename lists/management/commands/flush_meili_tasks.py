from django.core.management import BaseCommand

from django.conf import settings
from reports.models import Report
from reports.indexers.report_meili_indexer import ReportIndexer

from eqar_backend.meilisearch import MeiliClient

class Command(BaseCommand):
    help = 'Flush list of tasks in Meilisearch'

    PAGESIZE = 5000

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show report records, but do not actually delete")
        parser.add_argument("--only-deleted", "-d", action='store_true',
                            help="Only check index for deleted reports")
        parser.add_argument("--only-missing", "-m", action='store_true',
                            help="Only check for reports missing from the index")

    def handle(self, *args, **options):
        meili = MeiliClient()
        meili.wait_for(meili.meili.delete_tasks(parameters={'statuses': 'failed,canceled,succeeded'}))

