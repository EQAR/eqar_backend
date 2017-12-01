from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseAPITest(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'institution_resource',
                'association', 'country', 'language', 'qf_ehea_level', 'eter',
                'report_decision', 'report_status',
                'agency_demo_01', 'agency_demo_02',
                'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
                'report_demo_01',
                'programme_demo_01', 'programme_demo_02', 'programme_demo_03', 'programme_demo_04',
                'programme_demo_05', 'programme_demo_06', 'programme_demo_07', 'programme_demo_08',
                'programme_demo_09', 'programme_demo_10', 'programme_demo_11', 'programme_demo_12']

    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')

    def test_agency_list(self):
        """
            Test if we can display a list of agencies.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/browse/agencies/')
        self.assertEqual(response.data['count'], 2)

    def test_agency_browse(self):
        """
            Test if we can display a particular agency.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/browse/agencies/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['eqar_id'], 'EQARAG0021')

    def test_country_list(self):
        """
            Test if we can display a list of countries.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/browse/countries/')
        self.assertEqual(response.data['count'], 14)

    def test_country_browse(self):
        """
            Test if we can display a particular agency.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/browse/countries/64/')
        self.assertEqual(response.data['country_name_en'], 'Germany')