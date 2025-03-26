import json

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency, Agency
from reports.models import Report


class SubmissionAPIV2ReportTestWithContributingAgencies(APITestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'degree_outcome',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
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
        self.valid_data = {
            "agency": "ACQUIN",
            "contributing_agencies": ["EKKA"],
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activities": [
                {
                    "id": "2"
                }, {
                    "id": "7"
                }
            ],
            "status": "1",
            "decision": "1",
            "institutions": [
                {
                    "eter_id": "DE0392",
                    "identifier": "LOCAL001",
                    "resource": "local identifier"
                }
            ],
            "programmes": [
                {
                    "name_primary": "Programme name",
                    "degree_outcome": "1",
                    "qf_ehea_level": "1"
                }
            ]
        }
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@eqar.eu',
                                             password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')
        submitting_agency = SubmittingAgency.objects.get(pk=1)
        self.deqar_profile = DEQARProfile.objects.create(user=self.user, submitting_agency=submitting_agency)
        self.deqar_profile.save()

    def test_one_report_submission_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post(
            '/submissionapi/v2/submit/report',
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['submission_status'], 'success')
