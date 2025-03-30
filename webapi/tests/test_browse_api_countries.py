from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseCountryAPITest(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'identifier_resource',
                'association',
                'country_historical_field',
                'country_qa_requirement_type', 'country', 'country_historical_data_demo_01',
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

    def test_country_list(self):
        """
            Test if we can display a list of countries.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/')
        self.assertEqual(len(response.data), 49)

    def test_country_list_external_qaa_filter(self):
        """
            Test if we can display a list of countries with the external QAA filter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_1 = self.client.get('/webapi/v2/browse/countries/', {'external_qaa': 1})
        self.assertEqual(response_1.data[0]['name_english'], 'Armenia')

        response_2 = self.client.get('/webapi/v2/browse/countries/', {'external_qaa': 2})
        self.assertEqual(len(response_2.data), 32)

        response_3 = self.client.get('/webapi/v2/browse/countries/', {'external_qaa': 3})
        self.assertEqual(response_3.data[0]['name_english'], 'Albania')

    def test_country_list_european_approach_filter(self):
        """
            Test if we can display a list of countries with the external QAA filter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_1 = self.client.get('/webapi/v2/browse/countries/', {'european_approach': 1})
        self.assertEqual(response_1.data[0]['name_english'], 'Armenia')

        response_2 = self.client.get('/webapi/v2/browse/countries/', {'european_approach': 2})
        self.assertEqual(response_2.data[0]['name_english'], 'Albania')

        response_3 = self.client.get('/webapi/v2/browse/countries/', {'european_approach': 3})
        self.assertEqual(len(response_3.data), 0)

    def test_country_list_eqar_governmental_member(self):
        """
            Test if we can display a list of countries with the EQAR govermental member filter.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_true = self.client.get('/webapi/v2/browse/countries/', {'eqar_governmental_member': 'true'})
        self.assertEqual(len(response_true.data), 38)

        response_false = self.client.get('/webapi/v2/browse/countries/', {'eqar_governmental_member': 'false'})
        self.assertEqual(len(response_false.data), 11)

    def test_country_detail(self):
        """
            Test if we can display a particular country.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/64/')
        self.assertEqual(response.data['name_english'], 'Germany')
        self.assertEqual(len(response.data['historical_data']), 0)

    def test_country_detail_with_history(self):
        """
            Test if we can display a particular country with history.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/64/', {'history': 'true'})
        self.assertEqual(response.data['name_english'], 'Germany')
        self.assertEqual(len(response.data['historical_data']), 1)

    def test_country_reports_list(self):
        """
            Test if we can display a list of countries by reports.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/by-reports/')
        self.assertEqual(len(response.data), 1)

    def test_country_reports_list_with_history(self):
        """
            Test if we can display a list of countries by reports with historical data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/countries/by-reports/', {'history': 'true'})
        self.assertEqual(len(response.data), 3)
