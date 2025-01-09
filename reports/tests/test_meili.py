from django.conf import settings
from django.core.management import call_command
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from urllib.parse import urljoin
import requests

from reports.models import Report
from reports.indexers.report_meili_indexer import ReportIndexer

class ReportMeiliTest(APITestCase):
    """
    Test module for the Reports Meilisearch index
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'degree_outcome',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'other_provider_01', 'other_provider_02',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01',
        'report_demo_ap_01',
    ]

    def setUp(self):
        self.indexer = ReportIndexer()
        self.serializer = self.indexer.serializer()
        self.requests = requests.session()
        if hasattr(settings, "MEILI_API_KEY"):
            self.requests.headers.update({ 'authorization': f'Bearer {settings.MEILI_API_KEY}' })
        # index reports
        call_command('index_reports_meili')
        # create test user
        user = User.objects.create_superuser(username='testuser',
                                             email='testuser@eqar.eu',
                                             password='testpassword')
        user.save()
        token = Token.objects.get(user__username='testuser')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

    def test_check_meili(self):
        """
        check if reports are correctly indexed and run queries through Web API v2
        """
        # check index
        for report in Report.objects.all()[:4]:
            response = self.requests.get(urljoin(settings.MEILI_API_URL, f'indexes/{self.indexer.meili.INDEX_REPORTS}/documents/{report.id}'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), self.serializer.to_representation(report))

        # query Web API
        response = self.client.get('/webapi/v2/browse/reports/', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 13)
        self.assertEqual(response.data['facets']['facet_fields']['other_provider_covered_facet'], [ "false", 11, "true", 2 ])

        response = self.client.get('/webapi/v2/browse/reports/', { 'agency': 'ACQUIN' })
        self.assertEqual(response.data['count'], 13)
        response = self.client.get('/webapi/v2/browse/reports/', { 'agency_id': 5 })
        self.assertEqual(response.data['count'], 13)
        response = self.client.get('/webapi/v2/browse/reports/', { 'agency': 'DOESNOTEXIST' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'activity': 'System Accreditation in Germany' })
        self.assertEqual(response.data['count'], 2)
        response = self.client.get('/webapi/v2/browse/reports/', { 'activity_id': '2' })
        self.assertEqual(response.data['count'], 10)
        response = self.client.get('/webapi/v2/browse/reports/', { 'activity': '4711' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'activity_type': 'programme' })
        self.assertEqual(response.data['count'], 2)
        response = self.client.get('/webapi/v2/browse/reports/', { 'activity_type_id': 3 })
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/webapi/v2/browse/reports/', { 'activity_type_id': '4711' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'country': 'Germany' })
        self.assertEqual(response.data['count'], 12)
        response = self.client.get('/webapi/v2/browse/reports/', { 'country_id': '74' })
        self.assertEqual(response.data['count'], 6)
        response = self.client.get('/webapi/v2/browse/reports/', { 'country': 'Nomansland' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'status_id': 1 })
        self.assertEqual(response.data['count'], 12)
        response = self.client.get('/webapi/v2/browse/reports/', { 'status': 'voluntary' })
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/webapi/v2/browse/reports/', { 'status_id': 111 })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'decision_id': 1 })
        self.assertEqual(response.data['count'], 13)
        response = self.client.get('/webapi/v2/browse/reports/', { 'decision': 'negative' })
        self.assertEqual(response.data['count'], 0)
        response = self.client.get('/webapi/v2/browse/reports/', { 'decision_id': 4711 })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'language': 'English' })
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/webapi/v2/browse/reports/', { 'language_id': 40 })
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/webapi/v2/browse/reports/', { 'language_id': 47110 })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'cross_border': 'false' })
        self.assertEqual(response.data['count'], 7)

        response = self.client.get('/webapi/v2/browse/reports/', { 'ordering': 'valid_from', 'limit': 1, 'offset': '' })
        self.assertEqual(response.data['results'][0]['valid_from'], '2010-03-23T00:00:00Z')
        response = self.client.get('/webapi/v2/browse/reports/', { 'ordering': '-valid_to_calculated', 'limit': 1, 'offset': '' })
        self.assertEqual(response.data['results'][0]['valid_to'], '2030-09-30T00:00:00Z')

        response = self.client.get('/webapi/v2/browse/reports/', { 'limit': 0 })
        self.assertEqual(len(response.data['results']), 0)
        response = self.client.get('/webapi/v2/browse/reports/', { 'limit': -5 })
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/webapi/v2/browse/reports/', { 'offset': 'should be a number' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/reports/', { 'other_provider_covered': 'YES' })
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/webapi/v2/browse/reports/', { 'other_provider_covered': 'yes' })
        self.assertEqual(response.data['count'], 2)

        response = self.client.get('/webapi/v2/browse/reports/', { 'degree_outcome': 'false' })
        self.assertEqual(response.data['count'], 0)

        response = self.client.get('/webapi/v2/browse/reports/', { 'flag': 'high level' })
        self.assertEqual(response.data['count'], 0)

        response = self.client.get('/webapi/v2/browse/reports/', { 'year': '2014' })
        self.assertEqual(response.data['count'], 8)

        response = self.client.get('/webapi/v2/browse/reports/', { 'programme_type': 'Full recognised degree programme' })
        self.assertEqual(response.data['count'], 8)

        # delete last report
        self.indexer.delete(report.id)
        response = self.requests.get(urljoin(settings.MEILI_API_URL, f'indexes/{self.indexer.meili.INDEX_REPORTS}/documents/{report.id}'))
        self.assertEqual(response.status_code, 404)

