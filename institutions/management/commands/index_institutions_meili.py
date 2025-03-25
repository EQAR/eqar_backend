import meilisearch

from django.db.models import Q

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.conf import settings

from countries.models import Country
from institutions.models import Institution
from institutions.indexers.institution_meili_indexer import InstitutionIndexer


class Command(BaseCommand):
    help = 'Index Institution records (Meilisearch)'

    def add_arguments(self, parser):
        parser.add_argument('--country',
                            help='Index institutions from the specific country (ISO 3166 alpha-2 or alpha-3 code)', default=None)
        parser.add_argument('--sync',
                            help='Wait for the result of each Meilisearch API request.',
                            action='store_true')

    def handle(self, *args, **options):

        if options['country']:
            institutions = Institution.objects.filter(Q(
                    institutioncountry__country__iso_3166_alpha2=options['country']
                ) | Q(
                    institutioncountry__country__iso_3166_alpha3=options['country']
                ), institutioncountry__country_verified=True).distinct()
        else:
            institutions = Institution.objects.all()

        self.stdout.write(f'Indexing {institutions.count()} institutions:')
        indexer = InstitutionIndexer(sync=options['sync'])
        for hei in institutions.iterator():
            self.stdout.write(f'- {hei.deqar_id} {hei}')
            indexer.index(hei.id)

