from django.core.management import BaseCommand

from django.conf import settings
from reports.models import Report
from reports.indexers.report_meili_indexer import ReportIndexer

import meilisearch

class Command(BaseCommand):
    help = 'Delete reports from Meilisearch index that no longer exist'

    PAGESIZE = 5000

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show report records, but do not actually delete")
        parser.add_argument("--only-deleted", "-d", action='store_true',
                            help="Only check index for deleted reports")
        parser.add_argument("--only-missing", "-m", action='store_true',
                            help="Only check for reports missing from the index")

    def handle(self, *args, **options):
        if hasattr(settings, "MEILI_API_URL"):
            meili_url = getattr(settings, "MEILI_API_URL")
            meili_key = getattr(settings, "MEILI_API_KEY", None)
            self.meili_index = getattr(settings, "MEILI_INDEX_REPORTS", 'reports-v3')
            self.meili = meilisearch.Client(meili_url, meili_key)
            indexer = ReportIndexer(sync=False)
        else:
            raise ImproperlyConfigured("Meilisearch not configured")

        offset = 0
        total = 1
        in_meili = set()
        while offset < total:
            self.stdout.write(f"\rChecking report {offset}-{offset+self.PAGESIZE-1} of {total}", ending='')
            response = self.meili.index(self.meili_index).get_documents({ 'offset': offset, 'limit': self.PAGESIZE })
            if response.total > total:
                total = response.total
            for r in response.results:
                in_meili.add(int(r.id))
                if not options['only_missing']:
                    try:
                        Report.objects.get(id=r.id)
                    except Report.DoesNotExist:
                        self.stdout.write(f"\rdeleted report {r.id} still in Meili index: Agency {r.agency['acronym_primary']}, Activity ID {'/'.join([ str(i['id']) for i in r.agency_esg_activities])} @ {', '.join([ i['name_sort'] for i in r.institutions ])}")
                        if not options['dry_run']:
                            self.meili.index(self.meili_index).delete_document(r.id)
            offset += self.PAGESIZE

        self.stdout.write('')

        if not options['only_deleted']:
            missing_meili = 0
            for r in Report.objects.iterator():
                if r.id in in_meili:
                    self.stdout.write(f"\rReport {r.id} is in Meilisearch", ending='')
                else:
                    self.stdout.write(f"\rReport {r.id} is missing from Meilisearch!")
                    if not options['dry_run']:
                        indexer.index(r.id)
                    missing_meili += 1

            self.stdout.write(f'\r{missing_meili} reports were missing from Meilisearch in total.')

