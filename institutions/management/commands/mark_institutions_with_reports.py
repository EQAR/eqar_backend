from django.core.management import BaseCommand
from institutions.models import Institution


class Command(BaseCommand):
    help = 'Mark instiution records which appear in submitted reports.'

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show discrepancies, but do not change records.")

    def handle(self, *args, **options):
        institutions = Institution.objects.filter(reports__isnull=False)
        for institution in Institution.objects.iterator():
            count = institution.reports.count()
            if count > 0 and institution.has_report == False:
                self.stdout.write(self.style.WARNING(f'{institution.deqar_id} {institution} has {count} reports, but has_report was False.'))
                if not options['dry_run']:
                    institution.has_report = True
                    institution.save()
            elif count == 0 and institution.has_report == True:
                self.stdout.write(self.style.WARNING(f'{institution.deqar_id} {institution} has no reports, but has_report was True.'))
                if not options['dry_run']:
                    institution.has_report = False
                    institution.save()

