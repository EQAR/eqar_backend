from django.core.management import BaseCommand

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from institutions.models import InstitutionIdentifier
from agencies.models import Agency


class Command(BaseCommand):
    help = 'Find institution identifiers that are not unique, i.e. two or more institutions are identified by the same identifier'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Finding institution identifiers that are not unique...")

        for i in InstitutionIdentifier.objects.values('agency','identifier','resource').annotate(n=Count('institution')).filter(n__gt=1):
            try:
                qaa = Agency.objects.get(pk=i['agency'])
            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR(f"\nglobal identifier '{i['identifier']}' ({i['resource']}) is not unique") + ", it points to these institutions:")
                l = InstitutionIdentifier.objects.filter(identifier=i['identifier'], resource=i['resource'])
            else:
                self.stdout.write(self.style.WARNING(f"\n{qaa.acronym_primary}'s identifier '{i['identifier']}' is not unique") + ", it points to these institutions:")
                l = InstitutionIdentifier.objects.filter(identifier=i['identifier'], agency=qaa)
            for j in l:
                self.stdout.write(f"- DEQARINST{j.institution.deqar_id} {j.institution} ({j.institution.website_link})")

