from django.test import TestCase

from institutions.models import Institution, InstitutionHistoricalField


class InstitutionTestCase(TestCase):
    """
    Test module for the Institution classes.
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'flag', 'permission_type',
        'qf_ehea_level', 'eter_demo', 'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03'
    ]

    def test_institution_nqf_level_str(self):
        institution_nqf_level = Institution.objects.get(id=1).institutionnqflevel_set.first()
        self.assertEqual(str(institution_nqf_level), 'Level 6')

    def test_institution_qf_ehea_level_str(self):
        institution_qf_ehea_level = Institution.objects.get(id=1).institutionqfehealevel_set.first()
        self.assertEqual(str(institution_qf_ehea_level), 'first cycle')

    def test_institution_historical_field_str(self):
        ahf = InstitutionHistoricalField.objects.create(field='institutioncountries__country_id')
        self.assertEqual(str(ahf), 'institutioncountries__country_id')
