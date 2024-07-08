from django.core.management import BaseCommand

from django.conf import settings
from eqar_backend.searchers import Searcher
from institutions.models import Institution
from institutions.indexers.institution_indexer import InstitutionIndexer

import pysolr

class Command(BaseCommand):
    help = 'Delete institutions from Solr index that no longer exist'

    PAGESIZE = 1000

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show institution records, but do not actually delete")
        parser.add_argument("--only-deleted", "-d", action='store_true',
                            help="Only check index for deleted institutions")
        parser.add_argument("--only-missing", "-m", action='store_true',
                            help="Only check for institutions missing from the index")

    def handle(self, *args, **options):
        solr_core = getattr(settings, "SOLR_CORE_INSTITUTIONS", "deqar-institutions")
        solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        solr = pysolr.Solr(solr_url)

        searcher = Searcher(solr_core)

        offset = 0
        total = 1
        in_solr = set()
        while offset < total:
            self.stdout.write(f"\rChecking institution {offset}-{offset+self.PAGESIZE-1} of {total}", ending='')
            searcher.initialize({}, start=offset, rows_per_page=self.PAGESIZE)
            response = searcher.search()
            total = response.hits
            for r in response:
                in_solr.add(int(r['id']))
                if not options['only_missing']:
                    try:
                        Institution.objects.get(id=r['id'])
                    except Institution.DoesNotExist:
                        self.stdout.write(f"\rdeleted institution {r['id']} still in index: {r['deqar_id']} {r['name_primary']} ({r['website_link']})")
                        if not options['dry_run']:
                            solr.delete(id=r['id'], commit=True)
            offset += self.PAGESIZE

        self.stdout.write('')

        if not options['only_deleted']:
            missing = 0
            for r in Institution.objects.iterator():
                if r.id in in_solr:
                    self.stdout.write(f"\rInstitution {r.deqar_id} is in Solr", ending='')
                else:
                    self.stdout.write(f"\rInstitution {r.deqar_id} is missing from Solr!")
                    if not options['dry_run']:
                        indexer = InstitutionIndexer(r.id)
                        indexer.index()
                    missing += 1

            self.stdout.write(f'\r{missing} institutions were missing from Solr in total.')

