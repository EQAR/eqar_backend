from django.core.management import BaseCommand

from django.conf import settings
from eqar_backend.searchers import Searcher
from agencies.models import Agency
from agencies.indexers.agency_indexer import AgencyIndexer

import pysolr

class Command(BaseCommand):
    help = 'Delete agencies from Solr index that no longer exist'

    PAGESIZE = 20

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show agency records/documents, but do not actually delete")
        parser.add_argument("--only-deleted", "-d", action='store_true',
                            help="Only check index for deleted agencies")
        parser.add_argument("--only-missing", "-m", action='store_true',
                            help="Only check for agencies missing from the index")

    def handle(self, *args, **options):
        solr_core = getattr(settings, "SOLR_CORE_AGENCIES", "deqar-agencies")
        solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        solr = pysolr.Solr(solr_url)

        searcher = Searcher(solr_core)

        offset = 0
        total = 1
        counter = 0
        in_solr = set()
        while offset < total:
            self.stdout.write(f"\rChecking agency {offset}-{offset+self.PAGESIZE-1} of {total}", ending='')
            searcher.initialize({}, start=offset, rows_per_page=self.PAGESIZE)
            response = searcher.search()
            total = response.hits
            for r in response:
                in_solr.add(int(r['id']))
                if not options['only_missing']:
                    try:
                        Agency.objects.get(id=r['id'])
                    except Agency.DoesNotExist:
                        self.stdout.write(f"\rdeleted agency {r['id']} still in index: {r['deqar_id']} {r['name']} ({r['acronym']})")
                        counter += 1
                        if not options['dry_run']:
                            solr.delete(id=r['id'], commit=True)
            offset += self.PAGESIZE

        self.stdout.write(f'\n{counter} deleted agencies were still indexed in Solr.')

        if not options['only_deleted']:
            missing = 0
            for r in Agency.objects.iterator():
                if r.id in in_solr:
                    self.stdout.write(f"\rAgency {r.id} ({r.acronym_primary}) is in Solr", ending='')
                else:
                    self.stdout.write(f"\rAgency {r.id} ({r.acronym_primary}) is missing from Solr!")
                    if not options['dry_run']:
                        indexer = AgencyIndexer(r)
                        indexer.index()
                    missing += 1

            self.stdout.write(f'\r{missing} agencies were missing from Solr in total.')

