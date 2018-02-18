from django.test import TestCase

from institutions.models import Institution, InstitutionHistoricalField


class InstitutionTestCase(TestCase):
    """
    Test module for the Institution classes.
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'flag', 'permission_type',
        'qf_ehea_level', 'eter_demo', 'institution_historical_field',
        'agency_activity_type', 'agency_focus', 'identifier_resource',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',        'institution_demo_01', 'institution_demo_02', 'institution_demo_03'
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

    def test_institution_create_deqar_id(self):
        inst = Institution.objects.get(id=1)
        inst.create_deqar_id()
        self.assertEqual('DEQARINST0001', inst.deqar_id)

    def test_institution_set_flag_low(self):
        inst = Institution.objects.get(id=1)
        inst.set_flag_low()
        self.assertEqual('low level', inst.flag.flag)

    def test_institution_set_flag_high(self):
        inst = Institution.objects.get(id=1)
        inst.set_flag_high()
        self.assertEqual('high level', inst.flag.flag)

    def test_institution_name_add_source_note(self):
        inst_name = Institution.objects.get(id=1).institutionname_set.first()
        inst_name.add_source_note('source note')
        self.assertEqual('source note', inst_name.name_source_note)
        inst_name.add_source_note('source note 2')
        self.assertEqual('source note; source note 2', inst_name.name_source_note)

    def test_institution_name_version_add_source_note(self):
        inst_name = Institution.objects.get(id=1).institutionname_set.first()
        inst_name_ver = inst_name.institutionnameversion_set.create(name='Name Version')
        inst_name_ver.add_source_note('source note')
        self.assertEqual('source note', inst_name_ver.name_version_source_note)
        inst_name_ver.add_source_note('source note 2')
        self.assertEqual('source note; source note 2', inst_name_ver.name_version_source_note)

    def test_institution_location_add_source_note(self):
        inst_loc = Institution.objects.get(id=1).institutioncountry_set.first()
        inst_loc.add_source_note('source note')
        self.assertEqual('source note', inst_loc.country_source_note)
        inst_loc.add_source_note('source note 2')
        self.assertEqual('source note; source note 2', inst_loc.country_source_note)

    def test_institution_nqf_level_add_source_note(self):
        inst_nqf = Institution.objects.get(id=1).institutionnqflevel_set.first()
        inst_nqf.add_source_note('source note')
        self.assertEqual('source note', inst_nqf.nqf_level_source_note)
        inst_nqf.add_source_note('source note 2')
        self.assertEqual('source note; source note 2', inst_nqf.nqf_level_source_note)

    def test_institution_qf_ehea_level_add_source_note(self):
        inst_qf = Institution.objects.get(id=1).institutionqfehealevel_set.first()
        inst_qf.add_source_note('source note')
        self.assertEqual('source note', inst_qf.qf_ehea_level_source_note)
        inst_qf.add_source_note('source note 2')
        self.assertEqual('source note; source note 2', inst_qf.qf_ehea_level_source_note)
