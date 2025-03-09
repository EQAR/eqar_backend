from django.test import TestCase
from django.conf import settings
from django.core.management import call_command

from urllib.parse import urljoin
import requests

from reports.models import Report
from programmes.indexers.programme_indexer import ProgrammeIndexer

class ProgrammeMeiliTest(TestCase):
    """
    Test module for the Programmes Meilisearch index
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'degree_outcome',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def setUp(self):
        self.indexer = ProgrammeIndexer()
        self.serializer = self.indexer.serializer()
        self.requests = requests.session()
        if hasattr(settings, "MEILI_API_KEY"):
            self.requests.headers.update({ 'authorization': f'Bearer {settings.MEILI_API_KEY}' })
        # index programmes
        call_command('index_programmes')

    def test_index_report(self):
        # check index for sample of reports
        for report in Report.objects.filter(agency_esg_activities__activity_group__activity_type__type__in=[ 'programme', 'joint programme' ]):
            for programme in report.programme_set.all():
                response = self.requests.get(urljoin(settings.MEILI_API_URL, f'indexes/{self.indexer.meili.INDEX_PROGRAMMES}/documents/{programme.id}'))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), self.serializer.to_representation(programme))
        # delete last report
        self.indexer.delete(programme.id)
        response = self.requests.get(urljoin(settings.MEILI_API_URL, f'indexes/{self.indexer.meili.INDEX_PROGRAMMES}/documents/{programme.id}'))
        self.assertEqual(response.status_code, 404)

