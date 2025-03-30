from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from lxml import etree

class EuropassTest(APITestCase):
    """
    Test module for the Europass/QDR export
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')

    def test_europass_xml_creator(self):
        """
        Test generation of XML files for EDC
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get('/connectapi/v1/europass/accreditations-v2/DEU/', { "check": "false" })
        self.assertEqual(response['Content-Type'], 'application/xml')
        xml = etree.fromstring(response.content)
        self.assertEqual(xml.tag, '{http://data.europa.eu/snb/model/ap/ams-constraints/}Accreditations')

