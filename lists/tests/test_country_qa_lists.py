from pathlib import Path

import yaml
from django.apps import apps
from django.test import TestCase

FIXTURE = Path(__file__).resolve().parent.parent / 'fixtures' / 'country_qa_lists.yaml'


class CountryQAListsTestCase(TestCase):
    """
    The controlled lists for country QA requirements are seeded by migration lists/0010 from the fixture,
    so they exist without loading the fixture.
    """

    def test_lists_seeded_from_fixture(self):
        with FIXTURE.open() as f:
            entries = yaml.safe_load(f)
        self.assertEqual(len(entries), 48)
        for entry in entries:
            model = apps.get_model(entry['model'])
            self.assertEqual(model.objects.get(pk=entry['pk']).title, entry['fields']['title'])

    def test_str(self):
        model = apps.get_model('lists', 'CrossBorderPossibility')
        self.assertEqual(str(model.objects.get(pk=1)), 'Not possible')
