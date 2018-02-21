from django.core.management import BaseCommand

from agencies.models import Agency, SubmittingAgency, AgencyProxy


class Command(BaseCommand):
    help = 'Creates SubmittingAgency objects from existing agencies.'

    def handle(self, *args, **options):
        agency_set = Agency.objects.all()

        for agency in agency_set.iterator():
            submitting_agency, created = SubmittingAgency.objects.get_or_create(
                agency=agency,
                registration_from=agency.registration_start
            )

            agency_proxy, created = AgencyProxy.objects.get_or_create(
                submitting_agency=submitting_agency,
                allowed_agency=agency,
            )
            agency_proxy.proxy_from = agency.registration_start
            agency_proxy.save()

            print('Generating SubmittingAgency record to %s' % agency.acronym_primary)