from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseAPIInstitutionTest(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'identifier_resource',
                'association',
                'country_historical_field',
                'country_qa_requirement_type', 'country',
                'language', 'qf_ehea_level',
                'report_decision', 'report_status',
                'flag', 'permission_type', 'degree_outcome',
                'eqar_decision_type',
                'agency_historical_field',
                'agency_demo_01', 'agency_demo_02',
                'institution_historical_field',
                'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
                'users', 'report_demo_01',
                'programme_demo_01', 'programme_demo_02', 'programme_demo_03', 'programme_demo_04',
                'programme_demo_05', 'programme_demo_06', 'programme_demo_07', 'programme_demo_08',
                'programme_demo_09', 'programme_demo_10', 'programme_demo_11', 'programme_demo_12']

    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')

    def test_institution_identifier_resources_list(self):
        """
            Test if we can display indentifier resources.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/resources/')
        self.assertEqual(len(response.data), 2)
        self.assertEqual(len(list(filter(lambda x: x['resource'] == 'national identifier', response.data))), 1)

    def test_institution_identifier_detail(self):
        """
            Test if we can display an institution based on the identifier.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/by-identifier/national identifier/DE0001')
        self.assertEqual(response.data['id'], 1)

    def test_institution_identifier_detail_fail(self):
        """
            Test if we can display an institution based on the identifier.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/by-identifier/national identifier/DE0009')
        self.assertEqual(response.status_code, 404)

    def test_institution_eter_detail(self):
        """
            Test if we can display an institution based on the ETER ID.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/by-eter/DE0394/')
        self.assertEqual(response.data['id'], 2)

    def test_institution_eter_detail_fail(self):
        """
            Test if unknown ETER ID leads to failure.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/by-eter/DE4711/')
        self.assertEqual(response.status_code, 404)

    def test_institution_detail(self):
        """
            Test if we can display a particular institution.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/2/')
        self.assertEqual(response.data['website_link'], 'http://www.fh-guestrow.de')
