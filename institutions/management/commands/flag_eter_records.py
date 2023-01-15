from django.core.management.base import BaseCommand

from institutions.models import Institution


class Command(BaseCommand):
    help = 'Flag ETER records with missing QF-EHEA level.'

    def handle(self, *args, **options):
        institutions = Institution.objects.all()

        for institution in institutions:
            if institution.eter.ISCED_lowest == "":
                institution.set_flag_low()
