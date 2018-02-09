from django.apps import apps
from django.test import TestCase
from reports.apps import ReportsConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ReportsConfig.name, 'reports')
        self.assertEqual(apps.get_app_config('reports').name, 'reports')