from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseAPIInstitutionRelationshipTest(APITestCase):
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
                'institution_relationship_type',
                'institutions_hierarchical_relationship_demo', 'institutions_historical_relationship_demo',
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

    def test_institution_detail_historical_relationship(self):
        """
            Test if we can display an institution with historical relationship.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/2/')
        self.assertEqual(len(response.data['hierarchical_relationships']['part_of']), 1)

    def test_institution_detail_hierarchical_relationship(self):
        """
            Test if we can display an institution with hierarchical relationship.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v2/browse/institutions/1/')
        self.assertEqual(response.data['historical_relationships'][0]['relationship_type'], 'spun off')
