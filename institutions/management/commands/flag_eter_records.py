from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from agencies.models import Agency
from institutions.models import InstitutionETERRecord, Institution
from submissionapi.populators.institution_populator import InstitutionPopulator


class Command(BaseCommand):
    help = 'Flag ETER records with missing QF-EHEA level.'

    def handle(self, *args, **options):
        institutions = Institution.objects.all()

        for institution in institutions:
            if institution.eter.ISCED_lowest == "":
                institution.set_flag_low()
