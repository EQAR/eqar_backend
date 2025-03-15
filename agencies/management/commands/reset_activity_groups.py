import csv
import os

from django.core.management import BaseCommand

from agencies.models import AgencyActivityGroup, AgencyESGActivity


class Command(BaseCommand):
    help = 'Reset Agency Activity Group records.'

    def handle(self, *args, **options):
        activity_groups = {}
        reports_links = {}

        # Get the migration file path
        migration_dir = os.path.dirname(__file__)  # Directory of the migration file
        csv_path = os.path.join(migration_dir, 'csv', 'DEQARActivityGroups.csv')

        # Read the CSV and create a dictionary with the group names
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                activity_groups[row['activity_id']] = row['group_name']
                reports_links[row['activity_id']] = row['reports_link']

        for activity in AgencyESGActivity.objects.all():
            activity_group = activity_groups.get(str(activity.id))
            reports_link = reports_links.get(str(activity.id))

            if activity_group:
                group, created = AgencyActivityGroup.objects.get_or_create(
                    activity=activity_group,
                    activity_type=activity.activity_type,
                )
                if reports_link:
                    group.reports_link = reports_link
                    group.save()

            else:
                group = AgencyActivityGroup.objects.create(
                    activity=activity.activity if activity.activity else 'Other',
                    activity_type=activity.activity_type
                )

            activity.activity_group = group
            activity.save()

        # Clean "empty" activity groups
        AgencyActivityGroup.objects.filter(agencyesgactivity__isnull=True).delete()
