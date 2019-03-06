from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseAPIReportTest(APITestCase):
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

    def test_institutional_reports_list_by_institution(self):
        """
            Test if we can display a list of institutional reports by institution.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/reports/institutional/by-institution/3/')
        self.assertEqual(response.data['count'], 2)

        response = self.client.get('/webapi/v1/browse/reports/institutional/by-institution/3/', {'history': 'false'})
        self.assertEqual(response.data['count'], 1)

    def test_programme_reports_list_by_institution(self):
        """
            Test if we can display a list of programme reports by institution.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/reports/programme/by-institution/3/')
        self.assertEqual(response.data['count'], 7)

        response = self.client.get('/webapi/v1/browse/reports/programme/by-institution/3/', {'history': 'false'})
        self.assertEqual(response.data['count'], 3)
