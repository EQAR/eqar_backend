from django.conf import settings
from django.core.management import call_command
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from urllib.parse import urljoin
import requests

from institutions.models import Institution
from institutions.indexers.institution_meili_indexer import InstitutionIndexer


def solr2dict(f):
    """
    convert Solr-style facet field to dict for proper comparison
    """
    return { f[2*i]: f[2*i+1] for i in range(int(len(f)/2)) }

class InstitutionMeiliTest(APITestCase):
    """
    Test module for the Institutions Meilisearch index
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eqar_decision_type', 'language',
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
        self.indexer = InstitutionIndexer()
        self.serializer = self.indexer.serializer()
        self.requests = requests.session()
        if hasattr(settings, "MEILI_API_KEY"):
            self.requests.headers.update({ 'authorization': f'Bearer {settings.MEILI_API_KEY}' })
        # index reports
        call_command('index_institutions_meili', '--sync')
        # create test user
        user = User.objects.create_superuser(username='testuser',
                                             email='testuser@eqar.eu',
                                             password='testpassword')
        user.save()
        token = Token.objects.get(user__username='testuser')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token.key)

    def test_check_meili(self):
        """
        check if institutions are correctly indexed and run queries through Web API v2
        """
        # check index
        for institution in Institution.objects.all()[:5]:
            response = self.requests.get(urljoin(settings.MEILI_API_URL, f'indexes/{self.indexer.meili.INDEX_INSTITUTIONS}/documents/{institution.id}'))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), self.serializer.to_representation(institution))

        # query Connect API
        response = self.client.get('/connectapi/v1/institutions/', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        response = self.client.get('/connectapi/v1/providers/', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(solr2dict(response.data['facets']['facet_fields']['country_facet']), { "Germany": 3, "Austria": 1, "Hungary": 1, "Slovenia": 2 })

        # query Web API
        response = self.client.get('/webapi/v2/browse/institutions/', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(solr2dict(response.data['facets']['facet_fields']['other_provider_facet']), { "false": 3, "true": 2 })

        response = self.client.get('/webapi/v2/browse/institutions/', { 'agency': 'ACQUIN' })
        self.assertEqual(response.data['count'], 5)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'agency_id': 5 })
        self.assertEqual(response.data['count'], 5)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'agency': 'DOESNOTEXIST' })
        self.assertEqual(response.status_code, 400)

        """
        response = self.client.get('/webapi/v2/browse/institutions/', { 'activity': 'System Accreditation in Germany' })
        self.assertEqual(response.data['count'], 3)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'activity_id': '2' })
        self.assertEqual(response.data['count'], 4)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'activity': '4711' })
        self.assertEqual(response.status_code, 400)
        """

        response = self.client.get('/webapi/v2/browse/institutions/', { 'activity_type': 'joint programme' })
        self.assertEqual(response.data['count'], 2)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'activity_type_id': 2 })
        self.assertEqual(response.data['count'], 4)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'activity_type_id': '4711' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/institutions/', { 'country': 'Germany' })
        self.assertEqual(response.data['count'], 3)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'country_id': '74' })
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'country': 'Nomansland' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/institutions/', { 'status_id': 1 })
        self.assertEqual(response.data['count'], 4)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'status': 'voluntary' })
        self.assertEqual(response.data['count'], 2)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'status_id': 111 })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/institutions/', { 'qf_ehea_level_id': 2 })
        self.assertEqual(response.data['count'], 5)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'qf_ehea_level': 'second cycle' })
        self.assertEqual(response.data['count'], 1)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'qf_ehea_level_id': 111 })
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'qf_ehea_level': 'UNKNOWN-UNKNOWN' })
        self.assertEqual(response.data['count'], 0)

        response = self.client.get('/webapi/v2/browse/institutions/', { 'crossborder': 'true' })
        self.assertEqual(response.data['count'], 1)

        response = self.client.get('/webapi/v2/browse/institutions/', { 'ordering': 'name_sort', 'limit': 1, 'offset': '' })
        self.assertEqual(response.data['results'][0]['name_primary'], 'Academy for computer sciences Aaron Hillel Swartz')

        response = self.client.get('/webapi/v2/browse/institutions/', { 'limit': 0 })
        self.assertEqual(len(response.data['results']), 0)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'limit': -5 })
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'offset': 'should be a number' })
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/webapi/v2/browse/institutions/', { 'other_provider': 'YES' })
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/webapi/v2/browse/institutions/', { 'other_provider': 'yes' })
        self.assertEqual(response.data['count'], 2)

        # delete last report
        self.indexer.delete(institution.id)
        response = self.requests.get(urljoin(settings.MEILI_API_URL, f'indexes/{self.indexer.meili.INDEX_INSTITUTIONS}/documents/{institution.id}'))
        self.assertEqual(response.status_code, 404)

