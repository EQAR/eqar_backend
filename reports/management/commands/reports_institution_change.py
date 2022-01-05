from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from reports.tasks import index_report
from institutions.models import Institution
from reports.models import Report


class Command(BaseCommand):
    help = 'Reharvest files for report.'
    force = False

    def add_arguments(self, parser):
        parser.add_argument('--from', dest='institution_from',
                            help='ID of the institution that has to be changed.', default=None)
        parser.add_argument('--to', dest='institution_to',
                            help='ID of the institution that has to be newly assigned.', default=False)

    def handle(self, *args, **options):
        institution_from_id = options['institution_from']
        institution_to_id = options['institution_to']

        try:
            institution_from = Institution.objects.get(pk=institution_from_id)
        except ObjectDoesNotExist:
            raise CommandError('Institution (from) cannot be found .')

        try:
            institution_to = Institution.objects.get(pk=institution_to_id)
        except ObjectDoesNotExist:
            raise CommandError('Institution (to) cannot be found .')

        print("Changing %s to %s" % (institution_from.name_primary, institution_to.name_primary))

        reports = Report.objects.filter(institutions__id=institution_from_id)
        for report in reports.iterator():
            report.institutions.remove(institution_from)
            report.institutions.add(institution_to)

            # Saving report instance which triggers reports indexing.
            report.save()

            print("Modifying report %s" % report.id)

        print("Total %s report was modified!" % reports.count())
