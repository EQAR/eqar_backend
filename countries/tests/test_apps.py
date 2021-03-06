from django.apps import apps
from django.test import TestCase
from countries.apps import CountriesConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(CountriesConfig.name, 'countries')
        self.assertEqual(apps.get_app_config('countries').name, 'countries')