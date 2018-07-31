from django.core.management import BaseCommand
from agencies.models import AgencyESGActivity


class Command(BaseCommand):
    help = 'Set AgencyESGActivity name display.'

    def handle(self, *args, **options):
        activities = AgencyESGActivity.objects.all()
        for activity in activities:
            activity.save()
