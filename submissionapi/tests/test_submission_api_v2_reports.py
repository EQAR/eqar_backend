from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency, Agency
from reports.models import Report


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
                'eter_demo',
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
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@eqar.eu',
                                             password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')

    def test_report_delete_if_exists_with_rights(self):
        """
            Test if we can delete a non-existing report.
        """
        DEQARProfile.objects.create(user=self.user, submitting_agency_id=1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.delete('/submissionapi/v2/delete/report/2/')
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(pk=2)
        flag = report.reportflag_set.first()
        self.assertEqual(flag.flag_message, "Deletion was requested.")


    def test_report_delete_if_exists_without_rights(self):
        """
            Test if we can delete a non-existing report.
        """
        submitting_agency = SubmittingAgency.objects.create(agency=Agency.objects.get(pk=2))
        DEQARProfile.objects.create(user=self.user, submitting_agency=submitting_agency)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.delete('/submissionapi/v2/delete/report/2/')
        self.assertEqual(response.status_code, 403)


    def test_report_delete_if_not_exists_with_rights(self):
        """
            Test if we can delete a non-existing report.
        """
        DEQARProfile.objects.create(user=self.user, submitting_agency_id=1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.delete('/submissionapi/v2/delete/report/19/')
        self.assertEqual(response.status_code, 404)


    def test_report_delete_if_not_exists_without_rights(self):
        """
            Test if we can delete a non-existing report.
        """
        submitting_agency = SubmittingAgency.objects.create(agency=Agency.objects.get(pk=2))
        DEQARProfile.objects.create(user=self.user, submitting_agency=submitting_agency)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.delete('/submissionapi/v2/delete/report/19/')
        self.assertEqual(response.status_code, 404)
