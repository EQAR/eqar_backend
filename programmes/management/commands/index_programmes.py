import meilisearch

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand, CommandError
from django.conf import settings

from agencies.models import Agency
from reports.models import Report
from programmes.models import Programme
from programmes.indexers.programme_indexer import ProgrammeIndexer

class Command(BaseCommand):
    help = 'Index Programme records (Meilisearch)'

    def add_arguments(self, parser):
        parser.add_argument('--agency', dest='agency',
                            help='Index programme reports from one agency, specified by its acronym', default=None)
        parser.add_argument('--report', dest='report',
                            help='Index programmes covered in the report (by ID)', default=None)
        parser.add_argument('--institution', dest='institution',
                            help='Index programmes belonging to the institution (by ID)', default=None)

    def handle(self, *args, **options):

        if options['report']:
            try:
                report = Report.objects.get(id=options['report'])
            except ObjectDoesNotExist:
                raise CommandError('Report %s does not exist' % options['report'])
            programmes = report.programme_set.all()

        elif options['agency']:
            try:
                agency = Agency.objects.get(acronym_primary=options['agency'])
            except ObjectDoesNotExist:
                raise CommandError('Agency "%s" does not exist' % options['agency'])
            programmes = Programme.objects.filter(report__agency=agency)

        elif options['institution']:
            programmes = Programme.objects.filter(report__institutions__id=options['institution'])

        else:
            programmes = Programme.objects.all()

        self.stdout.write(f'Indexing {programmes.count()} programmes:')
        indexer = ProgrammeIndexer()
        for programme in programmes.iterator():
            self.stdout.write(f'- {programme.id} {programme.name_primary}')
            indexer.index(programme.id)

