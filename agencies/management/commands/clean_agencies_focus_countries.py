from django.core.management import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from agencies.models import Agency
from agencies.indexers.agency_indexer import AgencyIndexer
from countries.models import Country

class Command(BaseCommand):
    help = 'Clean up agency focus country lists based on existing reports.'

    def add_arguments(self, parser):
        parser.add_argument('AGENCY',
                            help='Agency/-ies for which to check (default: all)',
                            nargs='*', type=str)
        parser.add_argument('--dry-run', '-n',
                            help='Output changes that would be made, but do not save them',
                            action='store_true', default=False)

    def handle(self, *args, **options):

        if options['AGENCY']:
            agency_set = Agency.objects.filter(acronym_primary__in=options['AGENCY'])
        else:
            agency_set = Agency.objects.all()

        for agency in agency_set.iterator():
            changed = False
            self.stdout.write(f'- Checking agency {agency}:')

            # target set of countries from reports
            reports = { i['institutions__institutioncountry__country']: i['n'] for i in \
                agency.report_set.filter(institutions__institutioncountry__country_verified=True) \
                .values('institutions__institutioncountry__country').distinct().annotate(n=Count('id', distinct=True)) }

            # check if current focus countries all make sense
            for focus in agency.agencyfocuscountry_set.iterator():
                if focus.country_id in reports.keys():
                    if options['verbosity'] > 1:
                        self.stdout.write(f'  * {focus.country} : ok, {reports[focus.country_id]} reports')
                else:
                    if focus.country_is_official:
                        self.stdout.write(self.style.WARNING(f'  * {focus.country} : kept, no reports but official status'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  * {focus.country} : removed, no reports'))
                        changed = True
                        if not options['dry_run']:
                            focus.delete()

            # check if focus countries are missing
            for country in ( Country.objects.get(pk=i) for i in reports.keys() if i is not None ):
                try:
                    focus = agency.agencyfocuscountry_set.get(country=country)
                except ObjectDoesNotExist:
                    self.stdout.write(self.style.SUCCESS(f'  * {country} : added, {reports[country.id]} reports'))
                    changed = True
                    if not options['dry_run']:
                        focus = agency.agencyfocuscountry_set.create(country=country)
                        focus.country_is_crossborder = True
                        focus.save()

            # re-index if changed
            if changed and not options['dry_run']:
                self.stdout.write('  > re-indexing: ', ending='')
                indexer = AgencyIndexer(agency)
                indexer.index()

