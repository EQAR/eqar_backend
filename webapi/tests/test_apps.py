from django.apps import apps
from django.test import TestCase
from webapi.apps import DiscoveryApiConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(DiscoveryApiConfig.name, 'webapi')
        self.assertEqual(apps.get_app_config('webapi').name, 'webapi')