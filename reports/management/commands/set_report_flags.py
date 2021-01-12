from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError

from agencies.models import Agency
from reports.models import Report, ReportFlag
from submissionapi.tasks import recheck_flag


class Command(BaseCommand):
    help = 'Set Report record dates.'

    def add_arguments(self, parser):
        parser.add_argument('--report', dest='report_id',
                            help='The report ID of the Report.', default=0)
        parser.add_argument('--agency', dest='agency',
                            help='The acronym of the agency.', default=None)

    def handle(self, *args, **options):
        report_id = int(options['report_id'])
        agency = options['agency']

        if report_id != 0:
            try:
                report = Report.objects.get(id=report_id)
            except ObjectDoesNotExist:
                raise CommandError('Report ID "%s" does not exist' % report_id)


        if agency:
            try:
                agency = Agency.objects.get(acronym_primary=agency)
            except ObjectDoesNotExist:
                raise CommandError('Agency "%s" does not exist' % agency)

            reports = Report.objects.filter(agency=agency)
        else:
            reports = Report.objects.all()

        for report in reports.iterator():
            recheck_flag(report=report)
            print("Updating flags in report %s" % report.id)

        for report_flag in ReportFlag.objects.iterator():
            report_flag.created_at = report_flag.report.created_at
            report_flag.save()
