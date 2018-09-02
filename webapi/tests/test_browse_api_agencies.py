from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseAgencyAPITest(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'identifier_resource',
                'association',
                'country_historical_field',
                'country_qa_requirement_type', 'country',
                'flag', 'permission_type',
                'agency_historical_field',
                'agency_demo_01', 'agency_demo_02']

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
        self.assertEqual(response.data['count'], 1)

    def test_agency_detail(self):
        """
            Test if we can display a particular agency.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/5/')
        self.assertEqual(response.data['deqar_id'], 21)

    def test_agency_detail_with_history(self):
        """
            Test if we can display a particular agency with historical data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/5/')
        response_h = self.client.get('/webapi/v1/browse/agencies/5/', {'history': 'true'})
        self.assertEqual(len(response.data['activities']), 5)
        self.assertEqual(len(response_h.data['activities']), 6)

    def test_agency_list_by_location_country(self):
        """
            Test if we can display a list of agencies by country of location.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/based-in/64/')
        self.assertEqual(response.data['count'], 1)

    def test_agency_list_by_location_country_with_history(self):
        """
            Test if we can display a list of agencies by country of location.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/agencies/based-in/56/')
        response2 = self.client.get('/webapi/v1/browse/agencies/based-in/56/', {'history': 'true'})
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response2.data['count'], 1)


    def test_agency_list_by_country_focusing_to_without_history(self):
        """
            Test if we can display a list of agencies by country of focus without searching in historical data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_1 = self.client.get('/webapi/v1/browse/agencies/focusing-to/64/')
        response_2 = self.client.get('/webapi/v1/browse/agencies/focusing-to/74/')
        self.assertEqual(response_1.data['count'], 1)
        self.assertEqual(response_2.data['count'], 0)

    def test_agency_list_by_country_focusing_to_with_history(self):
        """
            Test if we can display a list of agencies by country of focus without searching in historical data.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response_1 = self.client.get('/webapi/v1/browse/agencies/focusing-to/64/', {'history': 'true'})
        response_2 = self.client.get('/webapi/v1/browse/agencies/focusing-to/74/', {'history': 'true'})
        self.assertEqual(response_1.data['count'], 1)
        self.assertEqual(response_2.data['count'], 1)
