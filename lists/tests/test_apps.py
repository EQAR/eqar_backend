from django.apps import apps
from django.test import TestCase
from lists.apps import ListsConfig


class AccountsConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(ListsConfig.name, 'lists')
        self.assertEqual(apps.get_app_config('lists').name, 'lists')