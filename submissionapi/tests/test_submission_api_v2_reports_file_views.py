import os

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

        self.data = {
            "file": self.base64_file_content,
            "file_name": "uploaded_report.pdf",
            "report_language": ["eng"]
        }

        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@eqar.eu',
                                             password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')
        submitting_agency = SubmittingAgency.objects.get(pk=1)
        self.deqar_profile = DEQARProfile.objects.create(user=self.user, submitting_agency=submitting_agency)
        self.deqar_profile.save()

    def test_report_file_creation(self):
        data = self.data
        data['report_id'] = 1
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post(
            '/submissionapi/v2/manage/report-file',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)

    def test_report_file_creation_report_id_missing(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post(
            '/submissionapi/v2/manage/report-file',
            data=self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 400, response.data)

    def test_report_file_update(self):
        data = self.data
        data['report_file_id'] = 1
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.put(
            '/submissionapi/v2/manage/report-file',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)

    def test_report_file_update_report_id_missing(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.put(
            '/submissionapi/v2/manage/report-file',
            data=self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 400, response.data)

    def test_report_file_delete_file(self):
        data = self.data
        data['report_file_id'] = 1

        ReportFile.objects.create(
            report_id=1,
            file_display_name="uploaded_report_no2.pdf",
        )

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.delete(
            '/submissionapi/v2/manage/report-file',
            data={'report_file_id': 1 },
            format='json'
        )
        self.assertEqual(response.status_code, 200, response.data)


    def test_report_file_delete_last_file(self):
        data = self.data
        data['report_file_id'] = 1
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.delete(
            '/submissionapi/v2/manage/report-file',
            data={'report_file_id': 1 },
            format='json'
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data['error'], "You can't delete the last file of a report. Please submit a new file first.", response.data)
