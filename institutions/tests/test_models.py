from django.test import TestCase

from institutions.models import Institution


class InstitutionTestCase(TestCase):
    """
    Test module for the Institution classes.
    """
    fixtures = [
        'country_qa_requirement_type', 'country',
        'qf_ehea_level', 'eter_demo',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03'
    ]

    def test_institution_country_str(self):
        institution_country = Institution.objects.get(id=1).institutioncountry_set.first()
        self.assertEqual(str(institution_country), 'Germany')

    def test_institution_nqf_level_str(self):
        institution_nqf_level = Institution.objects.get(id=1).institutionnqflevel_set.first()
        self.assertEqual(str(institution_nqf_level), 'Level 6')

    def test_institution_qf_ehea_level_str(self):
        institution_qf_ehea_level = Institution.objects.get(id=1).institutionqfehealevel_set.first()
        self.assertEqual(str(institution_qf_ehea_level), 'first cycle')
