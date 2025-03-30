import os

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
        'institution_hierarchical_relationship_type',
        'assessment',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'other_provider_01', 'other_provider_02',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def setUp(self):
        self.base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "csv_test_files")
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@eqar.eu',
                                             password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')
        submitting_agency = SubmittingAgency.objects.get(pk=1)
        self.deqar_profile = DEQARProfile.objects.create(user=self.user, submitting_agency=submitting_agency)
        self.deqar_profile.save()

    def test_csv_institutional(self):
        file = os.path.join(self.base_dir, "fulltest_inst.csv")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        with open(file, 'r') as csv_file:
            response = self.client.post(
                '/submissionapi/v2/submit/csv',
                data=csv_file.read(),
                content_type='text/csv',
            )
        self.assertEqual(response.status_code, 200, response.data)
        for line in response.data:
            self.assertEqual(line['submission_status'], 'success')

    def test_csv_programmes(self):
        file = os.path.join(self.base_dir, "fulltest_prog.csv")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        with open(file, 'r') as csv_file:
            response = self.client.post(
                '/submissionapi/v2/submit/csv',
                data=csv_file.read(),
                content_type='text/csv',
            )
        self.assertEqual(response.status_code, 200, response.data)
        for line in response.data:
            self.assertEqual(line['submission_status'], 'success')

    def test_csv_joint_programmes(self):
        file = os.path.join(self.base_dir, "fulltest_jp.csv")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        with open(file, 'r') as csv_file:
            response = self.client.post(
                '/submissionapi/v2/submit/csv',
                data=csv_file.read(),
                content_type='text/csv',
            )
        self.assertEqual(response.status_code, 200, response.data)
        for line in response.data:
            self.assertEqual(line['submission_status'], 'success')

    def test_csv_other_providers(self):
        file = os.path.join(self.base_dir, "fulltest_op.csv")
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        with open(file, 'r') as csv_file:
            response = self.client.post(
                '/submissionapi/v2/submit/csv',
                data=csv_file.read(),
                content_type='text/csv',
            )
        self.assertEqual(response.status_code, 200, response.data)
        for line in response.data:
            self.assertEqual(line['submission_status'], 'success')

