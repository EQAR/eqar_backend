from django.test import TestCase
from submissionapi.populators.populator import Populator


class PopulatorTestCase(TestCase):
    def test_init(self):
        populator = Populator(data={'agency': '1'})
        self.assertEqual(populator.data['agency'], "1")

