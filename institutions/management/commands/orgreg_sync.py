from django.core.management import BaseCommand

from institutions.orgreg.orgreg_synchronizer import OrgRegSynchronizer


class Command(BaseCommand):
    help = 'Sync institution records from OrgReg database.'

    def add_arguments(self, parser):
        parser.add_argument('--country', dest='country',
                            help='The two letter ISO code of the country.', default=None)
        parser.add_argument('--institution', dest='institution',
                            help='The ETER/OrgReg ID of the institution.', default=None)
        parser.add_argument('--all', dest='all',
                            help='Synchronize everything from OrgReg.', default=False)
        parser.add_argument('--only_new', dest='only_new',
                            help='Load only the "new" ones from OrgReg.', default=False)
        parser.add_argument('--dry-run', dest='dry_run',
                            help="Don't import anything, just show me a summary of what would happen.",
                            action='store_true')

    def handle(self, *args, **options):
        status = False
        orgreg_sync = OrgRegSynchronizer(only_new=options['only_new'], dry_run=options['dry_run'])

        if options['country']:
            status = orgreg_sync.collect_orgreg_ids_by_country(options['country'])

        if options['all']:
            status = orgreg_sync.collect_orgreg_ids_by_country(None)

        if options['institution']:
            status = orgreg_sync.collect_orgreg_ids_by_institution(options['institution'])

        if status:
            orgreg_sync.run()
        else:
            return "OrgReg record(s) can not be found with the defined criteria."