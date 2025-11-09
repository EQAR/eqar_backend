import os
import base64
import hashlib

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency, Agency
from reports.models import Report, ReportFile


class SubmissionAPIV2ReportTest(APITestCase):
    fixtures = ['agency_activity_type', 'agency_focus',
                'identifier_resource',
                'association',
                'country_historical_field',
                'country_qa_requirement_type', 'country',
                'language', 'qf_ehea_level',
                'report_decision', 'report_status',
                'flag', 'permission_type',
                'degree_outcome',
                'eqar_decision_type',
                'agency_historical_field',
                'agency_demo_01', 'agency_demo_02',
                'institution_historical_field',
                'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
                'users', 'report_demo_01',
                'submitting_agency_demo',
                'programme_demo_01', 'programme_demo_02', 'programme_demo_03', 'programme_demo_04',
                'programme_demo_05', 'programme_demo_06', 'programme_demo_07', 'programme_demo_08',
                'programme_demo_09', 'programme_demo_10', 'programme_demo_11', 'programme_demo_12']

    def setUp(self):
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.base64_file = os.path.join(self.current_dir, "file_base64", "file.txt")
        with open(self.base64_file, 'r') as file:
            self.base64_file_content = file.read().replace('\n', '')

        self.valid_data = {
            "agency": "ACQUIN",
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activities": [
                {
                    "id": "1"
                }
            ],
            "status": "1",
            "decision": "1",
            "report_files": [
                {
                    "file": self.base64_file_content,
                    "file_name": "uploaded_report.pdf",
                    "report_language": ["eng"]
                }
            ],
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
                    "qf_ehea_level": "1",
                    "degree_outcome": "1",
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

    def test_submit_report_with_embedded_file_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post(
            '/submissionapi/v2/submit/report',
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)
        report_id = response.data["submitted_report"]["id"]
        checksum_expected = hashlib.md5(base64.b64decode(self.base64_file_content)).hexdigest()
        self.assertEqual(ReportFile.objects.get(report__id=report_id).file_checksum, checksum_expected)

    def test_submit_report_with_embedded_file_missing_file_name(self):
        data = self.valid_data
        data['report_files'][0].pop('file_name')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post(
            '/submissionapi/v2/submit/report',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 400, response.data)
