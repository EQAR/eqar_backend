from django.core.management import BaseCommand
from django.conf import settings

from reports.models import Report

class Command(BaseCommand):
    help = 'Check for reports that are not assigned to any institution'

    def handle(self, *args, **options):
        qs_all = Report.objects.all()
        qs_faulty = qs_all.filter(institutions__isnull=True)
        n_all = qs_all.count()
        n_faulty = qs_faulty.count()
        self.stdout.write(f'{n_faulty} of {n_all} Reports are not assigned to any institution:')
        for r in qs_faulty.iterator():
            id_or_uri = settings.DEQAR_REPORT_URI % r.id if hasattr(settings, 'DEQAR_REPORT_URI') else r.id
            self.stdout.write(f'- {id_or_uri} {" / ".join(r.get_activity_names()} : {r.valid_from} -> {r.valid_to}')

