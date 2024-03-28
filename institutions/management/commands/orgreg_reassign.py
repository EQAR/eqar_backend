from django.core.management import BaseCommand

import csv

from institutions.models import Institution

from submissionapi.csv_functions.csv_insensitive_dict_reader import DictReaderInsensitive

from institutions.orgreg.orgreg_synchronizer import OrgRegSynchronizer


class Command(BaseCommand):
    help = 'Reassign OrgReg IDs'

    def add_arguments(self, parser):
        parser.add_argument('FILE', help='CSV file with correct mapping OrgReg -> DEQARINST IDs')
        parser.add_argument('--delete', '-d',
                            help='Delete duplicate Institution records (i.e. those that previously were linked to those OrgReg IDs)',
                            action='store_true', default=False)
        parser.add_argument('--force', '-f',
                            help='Re-assign even if existing institutions have Reports attached, and re-assign those Reports accordingly',
                            action='store_true', default=False)
        parser.add_argument('--sync', '-s',
                            help='Call OrgReg sync immediately after re-assignment',
                            action='store_true', default=False)
        parser.add_argument('--wipe', '-w',
                            help='Wipe existing InstitutionName and InstitutionCountry records before OrgReg sync',
                            action='store_true', default=False)
        parser.add_argument('--dry-run', '-n', dest='dry_run',
                            help='Do not change anything, just show me a summary of what would happen',
                            action='store_true', default=False)

    def handle(self, *args, **options):
        if options['force']:
            raise NotImplemented('feature not yet implemented')

        # open CSV
        with open(options['FILE'], 'r') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(), delimiters=['\t', ',', ';'])
            csvfile.seek(0)
            reader = DictReaderInsensitive(csvfile)

            for line in reader:
                try:
                    new = Institution.objects.get(deqar_id=line['BAS.DEQARID'])
                except Institution.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Institution with deqar_id [{line["BAS.DEQARID"]}] does not exist'))
                else:
                    if new.eter_id == line['BAS.ENTITYID']:
                        self.stdout.write(self.style.WARNING(f'{new.deqar_id} {new} already linked to {new.eter_id}'))
                    elif new.eter_id is not None:
                        self.stdout.write(self.style.ERROR(f'{new.deqar_id} {new} is already linked to {new.eter_id}, will not link to {line["BAS.ENTITYID"]}'))
                    else:
                        new.eter_id = line['BAS.ENTITYID']
                        self.stdout.write(self.style.SUCCESS(f'Linking {new.deqar_id} {new} to {new.eter_id} {line["BAS.ENTITYNAME"]}'))
                        try:
                            old = Institution.objects.get(eter_id=line['BAS.ENTITYID'])
                        except Institution.DoesNotExist:
                            self.stdout.write(f'  ({line["BAS.ENTITYID"]} was not linked to any other institution before.)')
                        else:
                            self.stdout.write(f'  ({line["BAS.ENTITYID"]} unlinked from {old.deqar_id} {old})')
                            old.eter_id = None
                            if not options['dry_run']:
                                old.save()
                            if rc := old.reports.count():
                                self.stdout.write(self.style.WARNING(f'  {old.deqar_id} already had {rc} reports linked to it.'))
                            elif options['delete']:
                                self.stdout.write(f'  (deleting {old.deqar_id} {old})')
                                if not options['dry_run']:
                                    old.delete()
                        if not options['dry_run']:
                            new.save()
                        if options['sync']:
                            orgreg_sync = OrgRegSynchronizer(only_new=False, dry_run=options['dry_run'])
                            if status := orgreg_sync.collect_orgreg_ids_by_institution(new.eter_id):
                                if options['wipe']:
                                    for i in new.institutionname_set.all():
                                        self.stdout.write(f'  (deleting name: {i.name_english or i.name_official}, valid to: {i.name_valid_to or "current"})')
                                    for l in new.institutioncountry_set.all():
                                        self.stdout.write(f'  (deleting location: {l.city}, {l.country})')
                                    if not options['dry_run']:
                                        new.institutionname_set.all().delete()
                                        new.institutioncountry_set.all().delete()
                                orgreg_sync.run()
                            else:
                                self.stdout.write(self.style.ERROR(f'  {new.eter_id} not found by OrgReg API'))

