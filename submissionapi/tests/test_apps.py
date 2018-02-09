from django.apps import apps
from django.test import TestCase
from submissionapi.apps import SubmissionapiConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(SubmissionapiConfig.name, 'submissionapi')
        self.assertEqual(apps.get_app_config('submissionapi').name, 'submissionapi')