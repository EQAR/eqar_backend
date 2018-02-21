from django.apps import apps
from django.test import TestCase
from institutions.apps import InstitutionsConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(InstitutionsConfig.name, 'institutions')
        self.assertEqual(apps.get_app_config('institutions').name, 'institutions')