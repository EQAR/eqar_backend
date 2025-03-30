from django.test import TestCase, RequestFactory
from unittest.mock import patch, MagicMock
from accounts.models import DEQARProfile
from reports.models import ReportFile, Report
from agencies.models import Agency
from submissionapi.permissions import CanSubmitToAgency

class CanSubmitToAgencyTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.id = 1
        self.request = self.factory.get('/some-url')
        self.request.user = self.user
        self.view = MagicMock()
        self.view.kwargs = {'pk': 1}
        self.permission = CanSubmitToAgency()

    @patch('accounts.models.DEQARProfile.objects.get')
    @patch('reports.models.ReportFile.objects.get')
    def test_allows_submission_if_user_is_allowed(self, mock_get_report_file, mock_get_deqar_profile):
        mock_deqar_profile = MagicMock()
        mock_deqar_profile.submitting_agency.agency_allowed.return_value = True
        mock_get_deqar_profile.return_value = mock_deqar_profile
        mock_report_file = MagicMock()
        mock_report_file.report.agency = Agency()
        mock_get_report_file.return_value = mock_report_file

        self.assertTrue(self.permission.has_permission(self.request, self.view))

    @patch('accounts.models.DEQARProfile.objects.get')
    @patch('reports.models.ReportFile.objects.get')
    def test_denies_submission_if_user_is_not_allowed(self, mock_get_report_file, mock_get_deqar_profile):
        mock_deqar_profile = MagicMock()
        mock_deqar_profile.submitting_agency.agency_allowed.return_value = False
        mock_get_deqar_profile.return_value = mock_deqar_profile
        mock_report_file = MagicMock()
        mock_report_file.report.agency = Agency()
        mock_get_report_file.return_value = mock_report_file

        self.assertFalse(self.permission.has_permission(self.request, self.view))

    @patch('accounts.models.DEQARProfile.objects.get')
    @patch('reports.models.ReportFile.objects.get')
    def test_denies_submission_if_report_file_does_not_exist(self, mock_get_report_file, mock_get_deqar_profile):
        mock_get_report_file.side_effect = ReportFile.DoesNotExist
        mock_get_deqar_profile.return_value = MagicMock()

        self.assertFalse(self.permission.has_permission(self.request, self.view))

    @patch('accounts.models.DEQARProfile.objects.get')
    def test_denies_submission_if_deqar_profile_does_not_exist(self, mock_get_deqar_profile):
        mock_get_deqar_profile.side_effect = DEQARProfile.DoesNotExist

        self.assertFalse(self.permission.has_permission(self.request, self.view))