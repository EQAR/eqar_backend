import pysolr
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.conf import settings

from agencies.models import Agency
from reports.indexers.reports_indexer import ReportsIndexer
from reports.models import Report


class Command(BaseCommand):
    help = 'Index Report records.'

    def add_arguments(self, parser):
        parser.add_argument('--agency', dest='agency',
                            help='The acronym of the agency.', default=None)
        parser.add_argument('--report', dest='report',
                            help='The ID of the report.', default=None)

    def handle(self, *args, **options):
        solr_core = getattr(settings, "SOLR_CORE_REPORTS", "deqar-reports")
        solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), solr_core)
        solr = pysolr.Solr(solr_url)
        # solr.delete(q='*:*', commit=True)

        agency = options['agency']
        report = options['report']

        if agency:
            try:
                agency = Agency.objects.get(acronym_primary=agency)
            except ObjectDoesNotExist:
                raise CommandError('Agency "%s" does not exist' % agency)
            reports = Report.objects.filter(agency=agency)

        elif report:
            reports = Report.objects.filter(id=report)

        else:
            reports = Report.objects.all()

        for report in reports.iterator():
            indexer = ReportsIndexer(report)
            indexer.index()
