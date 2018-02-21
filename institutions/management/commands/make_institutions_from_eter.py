from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from agencies.models import Agency
from institutions.models import InstitutionETERRecord, Institution
from submissionapi.populators.institution_populator import InstitutionPopulator


class Command(BaseCommand):
    help = 'Populates instiution records form eter records.'

    def handle(self, *args, **options):
        populator = InstitutionPopulator(
            submission={},
            agency=Agency.objects.get(pk=1)
        )

        eter_records = InstitutionETERRecord.objects.all()

        for eter in eter_records.iterator():
            try:
                Institution.objects.get(eter=eter)
            except ObjectDoesNotExist:
                populator._institution_create_from_eter(eter)
                print("%s is created" % populator.institution.name_primary)