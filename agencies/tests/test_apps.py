from django.apps import apps
from django.test import TestCase
from agencies.apps import AgenciesConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(AgenciesConfig.name, 'agencies')
        self.assertEqual(apps.get_app_config('agencies').name, 'agencies')