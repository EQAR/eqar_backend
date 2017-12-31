from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseAPITest(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'identifier_resource',
                'association',
                'country_qa_requirement_type','country',
                'language', 'qf_ehea_level',
                'report_decision', 'report_status',
                'eter_demo',
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
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/')
        self.assertEqual(response.data['count'], 2)

    def test_agency_detail(self):
        """
            Test if we can display a particular agency.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/1/')
        self.assertEqual(response.data['deqar_id'], 'EQARAG0021')

    def test_agency_list_by_operation_country(self):
        """
            Test if we can display a list of agencies by country of focus.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/operating-in/64/')
        self.assertEqual(response.data['count'], 1)

    def test_agency_list_by_location_country(self):
        """
            Test if we can display a list of agencies by country of location.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/based-in/64/')
        self.assertEqual(response.data['count'], 1)

    def test_country_list(self):
        """
            Test if we can display a list of countries.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/countries/')
        self.assertEqual(response.data['count'], 14)

    def test_country_list_by_agency(self):
        """
            Test if we can display a list of focus countries by agency.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/countries/by-agency/2/')
        self.assertEqual(response.data['count'], 2)

    def test_country_detail(self):
        """
            Test if we can display a particular agency.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/countries/64/')
        self.assertEqual(response.data['name_english'], 'Germany')

    def test_institution_list(self):
        """
            Test if we can display a list of institutions.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/')
        self.assertEqual(response.data['count'], 3)

    def test_institution_detail(self):
        """
            Test if we can display a particular institution.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/2/')
        self.assertEqual(response.data['website_link'], 'http://www.fh-guestrow.de')

    def test_institution_list_by_country(self):
        """
            Test if we can display a list of institutions by country.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/by-country/64/')
        self.assertEqual(response.data['count'], 3)

    def test_reports_list_by_agency(self):
        """
            Test if we can display a list of reports by agency.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/reports/by-agency/1/')
        self.assertEqual(response.data['count'], 12)

    def test_reports_list_by_institution(self):
        """
            Test if we can display a list of reports by institution.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/reports/by-institution/2/')
        self.assertEqual(response.data['count'], 3)

    def test_reports_list_by_country(self):
        """
            Test if we can display a list of reports by country.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/reports/by-country/64/')
        self.assertEqual(response.data['count'], 12)

    def test_reports_detail(self):
        """
            Test if we can display a particular report.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/reports/3/')
        self.assertEqual(response.data['local_identifier'], 'EQARAG0021-EQARIN0002-02')
