from django.core.management import BaseCommand
from institutions.models import Institution


class Command(BaseCommand):
    help = 'Mark instiution records which appear in submitted reports.'

    def handle(self, *args, **options):
        institutions = Institution.objects.filter(reports__isnull=False)
        for institution in institutions:
            institution.has_report = True
            institution.save()
