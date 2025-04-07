from django.core.management import BaseCommand

from django.conf import settings
from reports.models import Report
from reports.indexers.report_meili_indexer import ReportIndexer

from eqar_backend.meilisearch import MeiliClient

class Command(BaseCommand):
    help = 'Flush list of tasks in Meilisearch'

    PAGESIZE = 5000

    def add_arguments(self, parser):
        parser.add_argument('status',
                            nargs='*',
                            default=['failed','canceled','succeeded'],
                            choices=['enqueued', 'processing', 'succeeded', 'failed', 'canceled'],
                            help="Specify tasks with which status to delete (default: failed,canceled,succeeded)")

    def handle(self, status, *args, **options):
        self.stdout.write(f"Clearing tasks with the following statuses: {', '.join(status)}")
        meili = MeiliClient()
        tinfo = meili.wait_for(meili.meili.delete_tasks(parameters={'statuses': ','.join(status)}))
        self.stdout.write(f"Status={tinfo.status} Duration={tinfo.duration}")

