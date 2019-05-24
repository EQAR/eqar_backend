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
                'flag', 'permission_type',
                'eter_demo',
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

    def test_institution_list(self):
        """
            Test if we can display a list of institutions.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/')
        self.assertEqual(response.data['count'], 3)

    def test_institution_list_query(self):
        """
            Test if we can display a list of institutions with query parameter and historical data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'query': 'Wiesbaden'})
        self.assertEqual(response.data['count'], 1)

        response_wh_1 = self.client.get('/webapi/v1/browse/institutions/', {'query': 'München'})
        self.assertEqual(response_wh_1.data['count'], 1)

        response_wh_2 = self.client.get('/webapi/v1/browse/institutions/', {'query': 'München', 'history': 'false'})
        self.assertEqual(response_wh_2.data['count'], 0)

    def test_institution_agency_filter(self):
        """
            Test if we can display a list of institutions with agency filter parameter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'agency': '5'})
        self.assertEqual(response.data['count'], 3)

    def test_institution_country_filter(self):
        """
            Test if we can display a list of institutions with country filter parameter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'country': '64'})
        self.assertEqual(response.data['count'], 3)

        response_2 = self.client.get('/webapi/v1/browse/institutions/', {'country': '10'})
        self.assertEqual(response_2.data['count'], 1)

        response_wh = self.client.get('/webapi/v1/browse/institutions/', {'country': '10', 'history': 'false'})
        self.assertEqual(response_wh.data['count'], 0)

    def test_institution_qf_ehea_level_filter(self):
        """
            Test if we can display a list of institutions with QF EHEA level filter parameter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'qf_ehea_level': '2'})
        self.assertEqual(response.data['count'], 3)

        response = self.client.get('/webapi/v1/browse/institutions/', {'qf_ehea_level': '3'})
        self.assertEqual(response.data['count'], 1)

        response = self.client.get('/webapi/v1/browse/institutions/', {'qf_ehea_level': '3', 'history': 'false'})
        self.assertEqual(response.data['count'], 0)

    def test_institution_status_filter(self):
        """
            Test if we can display a list of institutions with status filter parameter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'status': '1'})
        self.assertEqual(response.data['count'], 3)

    def test_institution_country_is_crossborder(self):
        """
            Test if we can display a list of institutions with country_is_crossborder filter parameter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'focus_country_is_crossborder': 'false'})
        self.assertEqual(response.data['count'], 3)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'focus_country_is_crossborder': 'true'})
        self.assertEqual(response.data['count'], 3)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'focus_country_is_crossborder': 'true',
                                                                       'history': 'false'})
        self.assertEqual(response.data['count'], 0)

    def test_institution_report_year(self):
        """
            Test if we can display a list of institutions with report year filter parameter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'report_year': 'invalid'})
        self.assertEqual(response.data['count'], 0)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/', {'report_year': '2010'})
        self.assertEqual(response.data['count'], 2)

    def test_institution_detail(self):
        """
            Test if we can display a particular institution.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/2/')
        self.assertEqual(response.data['website_link'], 'http://www.fh-guestrow.de')
