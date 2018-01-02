from django.test import TestCase

from countries.models import Country, CountryHistoricalField


class CountryTestCase(TestCase):
    """
    Test module for the Country class.
    """
    fixtures = [
        'country_qa_requirement_type',
        'country',
    ]

    def test_country_str(self):
        country = Country.objects.get(id=1)
        self.assertEqual(str(country), 'Afghanistan')

    def test_qa_requirement_type_str(self):
        country = Country.objects.get(id=1)
        self.assertEqual(str(country.qa_requirement_type), 'institutional and programme level')

    def test_country_historical_field_str(self):
        ahf = CountryHistoricalField.objects.create(field='eligibility')
        self.assertEqual(str(ahf), 'eligibility')
