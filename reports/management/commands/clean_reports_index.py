from django.core.management import BaseCommand

from django.conf import settings
from eqar_backend.searchers import Searcher
from reports.models import Report
from reports.indexers.reports_indexer import ReportsIndexer

import pysolr

class Command(BaseCommand):
    help = 'Delete reports from Solr index that no longer exist'

    PAGESIZE = 5000

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show report records, but do not actually delete")
        parser.add_argument("--only-deleted", "-d", action='store_true',
                            help="Only check index for deleted reports")
        parser.add_argument("--only-missing", "-m", action='store_true',
                            help="Only check for reports missing from the index")

    def handle(self, *args, **options):
        solr_core = getattr(settings, "SOLR_CORE_REPORTS", "deqar-reports")
        solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        solr = pysolr.Solr(solr_url)

        searcher = Searcher(solr_core)

        offset = 0
        total = 1
        in_solr = set()
        while offset < total:
            self.stdout.write(f"\rChecking report {offset}-{offset+self.PAGESIZE-1} of {total}", ending='')
            searcher.initialize({}, start=offset, rows_per_page=self.PAGESIZE)
            response = searcher.search()
            total = response.hits
            for r in response:
                in_solr.add(int(r['id']))
                if not options['only_missing']:
                    try:
                        Report.objects.get(id=r['id'])
                    except Report.DoesNotExist:
                        self.stdout.write(f"\rdeleted report {r['id']} still in index: {r['agency_acronym']}, {r['activity_facet']} @ {', '.join(r['institution_programme_primary'])}")
                        if not options['dry_run']:
                            solr.delete(id=r['id'], commit=True)
            offset += self.PAGESIZE

        self.stdout.write('')

        if not options['only_deleted']:
            missing = 0
            for r in Report.objects.iterator():
                if r.id in in_solr:
                    self.stdout.write(f"\rReport {r.id} is in Solr", ending='')
                else:
                    self.stdout.write(f"\rReport {r.id} is missing from Solr!")
                    if not options['dry_run']:
                        indexer = ReportsIndexer(r.id)
                        indexer.index()
                    missing += 1

            self.stdout.write(f'\r{missing} reports were missing from Solr in total.')

