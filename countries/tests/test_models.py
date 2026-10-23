from django.test import TestCase

from countries.models import Country, CountryQARequirementType


class CountryTestCase(TestCase):
    """
    Test module for the Country class.
    """
    fixtures = [
        'flag',
        'permission_type',
        'country_qa_requirement_type',
        'country',
    ]

    def test_country_str(self):
        country = Country.objects.get(id=1)
        self.assertEqual(str(country), 'Afghanistan')

    def test_qa_requirement_type_str(self):
        crt = CountryQARequirementType.objects.get(id=1)
        self.assertEqual(str(crt.qa_requirement_type), 'institutional level')
