import meilisearch

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.conf import settings

from agencies.models import Agency
from reports.models import Report
from reports.indexers.report_meili_indexer import ReportIndexer

class Command(BaseCommand):
    help = 'Index Report records (Meilisearch)'

    def add_arguments(self, parser):
        parser.add_argument('--agency', dest='agency',
                            help='Index reports from one agency, specified by its acronym', default=None)
        parser.add_argument('--report', dest='report',
                            help='Index the report specified by ID', default=None)
        parser.add_argument('--institution', dest='institution',
                            help='Index reports covering the institution (by ID)', default=None)
        parser.add_argument('--sync',
                            help='Wait for the result of each Meilisearch API request.',
                            action='store_true')

    def handle(self, *args, **options):

        if options['report']:
            try:
                reports = Report.objects.filter(id=options['report'])
            except ObjectDoesNotExist:
                raise CommandError('Report %s does not exist' % options['report'])

        elif options['agency']:
            try:
                agency = Agency.objects.get(acronym_primary=options['agency'])
            except ObjectDoesNotExist:
                raise CommandError('Agency "%s" does not exist' % options['agency'])
            reports = Report.objects.filter(agency=agency)

        elif options['institution']:
            reports = Report.objects.filter(institutions__id=options['institution'])

        else:
            reports = Report.objects.all()

        self.stdout.write(f'Indexing {reports.count()} reports:')
        indexer = ReportIndexer(sync=options['sync'])
        for report in reports.iterator():
            self.stdout.write(f'- {report.id} {report.agency.acronym_primary}')
            indexer.index(report.id)

