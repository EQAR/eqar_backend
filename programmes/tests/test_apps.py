from django.apps import apps
from django.test import TestCase
from programmes.apps import ProgrammesConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ProgrammesConfig.name, 'programmes')
        self.assertEqual(apps.get_app_config('programmes').name, 'programmes')