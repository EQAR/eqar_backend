from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class BrowseAPIReportsAndInstitutionRelationshipTest(APITestCase):
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
                'institution_relationship_type',
                'users']

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
        response = self.client.get('/webapi/v1/browse/institutions/2/')
        self.assertEqual(len(response.data['hierarchical_relationships']['part_of']), 1)

    def test_institution_detail_hierarchical_relationship(self):
        """
            Test if we can display an institution with hierarchical relationship.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/webapi/v1/browse/institutions/1/')
        self.assertEqual(response.data['historical_relationships'][0]['relationship_type'], 'is spun off from')
