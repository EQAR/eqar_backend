from django.core.management import BaseCommand
from institutions.models import Institution


class Command(BaseCommand):
    help = 'Set instiution name sort.'

    def handle(self, *args, **options):
        institutions = Institution.objects.all()
        for institution in institutions:
            institution.save()
