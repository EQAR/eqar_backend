from django.core.management import BaseCommand

from institutions.models import Institution
from institutions.tasks import index_institution, meili_index_institution


class Command(BaseCommand):
    help = 'Reconcile the has_report flag of institution records with their actual (incl. related) reports.'

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", "-n", action='store_true',
                            help="Only show discrepancies, but do not change records.")
        parser.add_argument("--reindex", action='store_true',
                            help="Reindex (Solr + Meilisearch) the institutions whose flag changed.")

    def handle(self, *args, **options):
        changed = 0
        for institution in Institution.objects.iterator():
            expected = institution.calculate_has_report()
            if institution.has_report == expected:
                continue

            changed += 1
            self.stdout.write(self.style.WARNING(
                f'{institution.deqar_id} {institution} has_report was {institution.has_report}, '
                f'should be {expected}.'))

            if not options['dry_run']:
                Institution.objects.filter(pk=institution.pk).update(has_report=expected)
                if options['reindex']:
                    index_institution.delay(institution.pk)
                    meili_index_institution.delay(institution.pk)

        if options['dry_run']:
            self.stdout.write(f'{changed} institution(s) would be updated.')
        else:
            self.stdout.write(f'{changed} institution(s) updated.')
