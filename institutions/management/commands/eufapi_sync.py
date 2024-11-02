from collections import defaultdict

from requests import RequestException

from django.core.management import BaseCommand, CommandError

from django.db.models import Q

from institutions.eufapi.eufapi_synchronizer import HeiApiSynchronizer, EufApiError, ErasmusCodeSyntaxError, ErasmusCodeNotFound
from institutions.eufapi.picapi_synchronizer import PicApiSynchronizer, PicApiError, PicCodeNotFound
from institutions.models import Institution

class Command(BaseCommand):
    help = 'Sync institution identifiers from EUF HEI API.'

    def add_arguments(self, parser):
        parser.add_argument('--country',
                            help='The two letter ISO code of the country.',
                            default=None)
        parser.add_argument('--institution',
                            help='The DEQARINST ID of the institution.',
                            default=None)
        parser.add_argument('--all',
                            help='Synchronize everything from OrgReg.',
                            action='store_true')
        parser.add_argument('--skip-vat',
                            help='Do not get VAT IDs from EU Commission API.',
                            action='store_true')
        parser.add_argument('--vat-always',
                            help='Always query for VAT IDs (default: only when PIC code added or changed).',
                            action='store_true')
        parser.add_argument('--dry-run', '-n',
                            help="Don't import anything, just show me a summary of what would happen.",
                            action='store_true')

    def handle(self, country, institution, all, skip_vat, vat_always, dry_run, verbosity, *args, **options):
        # "global" options
        self.dry_run = dry_run
        self.verbosity = verbosity

        # select institutions to handle
        if institution:
            institutions = Institution.objects.filter(Q(id=institution) | Q(deqar_id=institution))
        elif country:
            institutions = Institution.objects.filter(institutioncountry__country__iso_3166_alpha2=country, institutioncountry__country_verified=True).distinct()
        elif all:
            institutions = Institution.objects.all()
        else:
            raise CommandError("You need to specify an institution, a country or pass --all/-a.")

        # EUF API syncer
        self.syncer = HeiApiSynchronizer()
        self.stdout.write('Loading HEIs from EUF API...')
        loaded = self.syncer.load()
        self.stdout.write(self.style.SUCCESS(f'{loaded["received"]} records received, {loaded["has_erasmus"]} had a (unique) Erasmus code'))
        if loaded['duplicate_erasmus']:
            self.stdout.write(self.style.WARNING(f'Duplicate Erasmus codes ignored:'))
            for d in loaded["duplicate_erasmus"]:
                self.stdout.write(self.style.WARNING(f'- {d}'))
        # PIC API syncer
        self.picapi = PicApiSynchronizer()

        # this is the main loop
        self.log = []
        self.stats = defaultdict(lambda: { 'added': 0, 'updated': 0, 'deleted': 0, 'notfound': 0, 'error': 0 })
        for hei in institutions:
            changes = self.handle_heiapi(hei)
            if skip_vat:
                pass
            elif changes and self.picapi.R_PIC in changes and changes[self.picapi.R_PIC][1] != changes[self.picapi.R_PIC][0]:
                self.handle_pic(hei, pic=changes[self.picapi.R_PIC][1])
            elif vat_always:
                self.handle_pic(hei)
            self.flush_log(hei)

        # print stats
        self.stdout.write(f'Stats\n=====\n')
        self.stdout.write(f'Type            Added  Updated  Deleted  Not found  Error')
        for resource in self.stats:
            self.stdout.write(f'{resource:15} '
                f'{self.stats[resource]["added"]:5d}  '
                f'{self.stats[resource]["updated"]:7d}  '
                f'{self.stats[resource]["deleted"]:7d}  '
                f'{self.stats[resource]["notfound"]:9d}  '
                f'{self.stats[resource]["error"]:5d}'
            )

    def report_change(self, resource, change):
        """
        add change to log
        """
        if change is not None:
            if change[0] is None:
                if change[1] is not None:
                    self.log.append(f'ADD - {resource}: {change[1]}')
                    self.stats[resource]['added'] += 1
                elif self.verbosity > 1:
                    self.log.append(f'[none] - {resource}')
            else:
                if change[1] is None:
                    self.log.append(f'DELETE - {resource}: {change[0]}')
                    self.stats[resource]['deleted'] += 1
                elif change[1] != change[0]:
                    self.log.append(f'UPDATE - {resource}: {change[0]} <- {change[1]}')
                    self.stats[resource]['updated'] += 1
                elif self.verbosity > 1:
                    self.log.append(f'[unchanged] - {resource}: {change[0]}')
        elif self.verbosity > 1:
            self.log.append(f'[none] - {resource}')


    def handle_heiapi(self, hei):
        """
        sync identifiers from EUF API
        """
        try:
            stats = self.syncer.sync(hei, dry_run=self.dry_run)
        except ErasmusCodeNotFound as error:
            self.log.append(self.style.WARNING(str(error)))
            self.stats[self.syncer.R_ERASMUS]['notfound'] += 1
        except ErasmusCodeSyntaxError as error:
            self.log.append(self.style.ERROR(str(error)))
            self.stats[self.syncer.R_ERASMUS]['error'] += 1
        else:
            if stats is None:
                self.report_change(self.syncer.R_ERASMUS, stats)
            else:
                for (key, change) in stats.items():
                    self.report_change(key, change)
            return stats


    def handle_pic(self, hei, pic=None):
        """
        sync EU VAT ID from PIC API
        """
        try:
            change = self.picapi.sync(hei, dry_run=self.dry_run, pic=pic)
        except PicCodeNotFound as error:
            self.log.append(self.style.WARNING(str(error)))
            self.stats[self.picapi.R_PIC]['notfound'] += 1
        except (RequestException, PicApiError) as error:
            self.log.append(self.style.ERROR(str(error)))
            self.stats[self.picapi.R_PIC]['error'] += 1
        else:
            self.report_change(self.picapi.R_VAT, change)
            return change


    def flush_log(self, hei):
        """
        print and empty log if there is anything to report
        """
        if self.log or self.verbosity > 1:
            self.stdout.write('-' * 100)
            self.stdout.write(f'Institution {hei.deqar_id}')
            self.stdout.write(hei.name_primary)
            self.stdout.write('-' * 100)
            for line in self.log:
                self.stdout.write(line)
            self.stdout.write('')
            self.log.clear()

