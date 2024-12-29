import json

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency, Agency
from reports.models import Report


class SubmissionAPIV1ReportTest(APITestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
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
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activity": "1",
            "status": "1",
            "decision": "1",
            "report_files": [
                {
                    "report_language": ["eng"]
                }
            ],
            "institutions": [
                {
                    "eter_id": "DE0392",
                    "identifiers": [
                        {
                            "identifier": "LOCAL001",
                            "resource": "local identifier"
                        }, {
                            "identifier": "DE0876",
                            "resource": "national identifier"
                        }
                    ]
                }
            ],
            "programmes": [
                {
                    "name_primary": "Programme name"
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
            '/submissionapi/v1/submit/report',
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['submission_status'], 'success')

    def test_multiple_report_submission_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        data2 = self.valid_data
        data2['valid_from'] = "2010-05-01"
        data_multiple = [self.valid_data, data2]
        response = self.client.post(
            '/submissionapi/v1/submit/report',
            data=data_multiple,
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data[0]['submission_status'], 'success')

    def test_one_report_submission_not_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        data = self.valid_data
        data['agency'] = "invalid agency"
        response = self.client.post(
            '/submissionapi/v1/submit/report',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data['submission_status'], 'errors')

    def test_multiple_report_submission_not_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        data1 = self.valid_data
        data1['agency'] = "invalid agency"
        data2 = self.valid_data
        data2['valid_from'] = "2010-05-01"
        data_multiple = [data1, data2]
        response = self.client.post(
            '/submissionapi/v1/submit/report',
            data=data_multiple,
            format='json'
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data[0]['submission_status'], 'errors')