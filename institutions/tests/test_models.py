import datetime
from django.test import TestCase

from institutions.models import Institution, InstitutionHistoricalField, InstitutionHistoricalRelationshipType, \
     InstitutionHierarchicalRelationshipType, InstitutionHierarchicalRelationship


class InstitutionTestCase(TestCase):
    """
    Test module for the Institution classes.
    """
    fixtures = [
        'country_qa_requirement_type', 'country', 'flag', 'permission_type',
        'qf_ehea_level', 'eter_demo', 'institution_historical_field',
        'agency_activity_type', 'agency_focus', 'identifier_resource',
        'agency_historical_field',
        'eqar_decision_type',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03', 'institution_demo_closed',
        'institution_relationship_type', 'institution_hierarchical_relationship_type'
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
        inst = Institution.objects.create(
            name_primary='Tet Institution',
            website_link='http://www.example.com',
        )
        inst.create_deqar_id()
        self.assertEqual('DEQARINST%04d' % inst.id, inst.deqar_id)

    def test_institution_create_deqar_id_for_AP(self):
        inst = Institution.objects.create(
            name_primary='Tet Institution',
            website_link='http://www.example.com',
            is_alternative_provider=True
        )
        inst.create_deqar_id()
        self.assertEqual('DEQARINSTAP%04d' % inst.id, inst.deqar_id)

    def test_institution_set_flag_low(self):
        inst = Institution.objects.get(id=1)
        inst.set_flag_low()
        self.assertEqual('low level', inst.flag.flag)
        inst.set_flag_high()
        inst.set_flag_low()
        self.assertEqual('high level', inst.flag.flag)

    def test_institution_set_flag_high(self):
        inst = Institution.objects.get(id=1)
        inst.set_flag_high()
        self.assertEqual('high level', inst.flag.flag)

    def test_institution_name_add_source_note(self):
        cur_date = datetime.date.today().strftime("%Y-%m-%d")
        inst_name = Institution.objects.get(id=1).institutionname_set.first()
        msg1 = 'source note'
        msg2 = 'source note 2'
        inst_name.add_source_note(msg1)
        self.assertEqual('%s on [%s]' % (msg1, cur_date), inst_name.name_source_note)
        inst_name.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date),
                         inst_name.name_source_note)
        inst_name.add_source_note(msg1)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date),
                         inst_name.name_source_note)

    def test_institution_name_version_add_source_note(self):
        cur_date = datetime.date.today().strftime("%Y-%m-%d")
        inst_name = Institution.objects.get(id=1).institutionname_set.first()
        inst_name_ver = inst_name.institutionnameversion_set.create(name='Name Version')
        msg1 = 'source note'
        msg2 = 'source note 2'
        inst_name_ver.add_source_note(msg1)
        self.assertEqual('%s on [%s]' % (msg1, cur_date), inst_name_ver.name_version_source_note)
        inst_name_ver.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date),
                         inst_name_ver.name_version_source_note)
        inst_name_ver.add_source_note(msg1)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date),
                         inst_name_ver.name_version_source_note)

    def test_institution_location_add_source_note(self):
        cur_date = datetime.date.today().strftime("%Y-%m-%d")
        inst_loc = Institution.objects.get(id=1).institutioncountry_set.first()
        msg1 = 'source note'
        msg2 = 'source note 2'
        inst_loc.add_source_note(msg1)
        self.assertEqual('%s on [%s]' % (msg1, cur_date), inst_loc.country_source_note)
        inst_loc.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date), inst_loc.country_source_note)
        inst_loc.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date), inst_loc.country_source_note)

    def test_institution_nqf_level_add_source_note(self):
        cur_date = datetime.date.today().strftime("%Y-%m-%d")
        inst_nqf = Institution.objects.get(id=1).institutionnqflevel_set.first()
        msg1 = 'source note'
        msg2 = 'source note 2'
        inst_nqf.add_source_note(msg1)
        self.assertEqual('%s on [%s]' % (msg1, cur_date), inst_nqf.nqf_level_source_note)
        inst_nqf.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date), inst_nqf.nqf_level_source_note)
        inst_nqf.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date), inst_nqf.nqf_level_source_note)

    def test_institution_qf_ehea_level_add_source_note(self):
        cur_date = datetime.date.today().strftime("%Y-%m-%d")
        inst_qf = Institution.objects.get(id=1).institutionqfehealevel_set.first()
        msg1 = 'source note'
        msg2 = 'source note 2'
        inst_qf.add_source_note(msg1)
        self.assertEqual('%s on [%s]' % (msg1, cur_date), inst_qf.qf_ehea_level_source_note)
        inst_qf.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date), inst_qf.qf_ehea_level_source_note)
        inst_qf.add_source_note(msg2)
        self.assertEqual('%s on [%s]; %s on [%s]' % (msg1, cur_date, msg2, cur_date), inst_qf.qf_ehea_level_source_note)

    def test_institution_historical_relationship_type_str(self):
        relationship_type = InstitutionHistoricalRelationshipType.objects.get(id=1)
        self.assertEqual(str(relationship_type), '=> precedes / succeeds <=')

    def test_institution_set_primary_name_ongoing(self):
        inst = Institution.objects.get(id=3)
        inst.set_primary_name()
        inst.save()
        self.assertEqual(inst.name_primary, 'Hessische Hochschule für Polizei und Verwaltung')

    def test_institution_set_primary_closed(self):
        inst = Institution.objects.get(id=4)
        inst.set_primary_name()
        inst.save()
        self.assertEqual(inst.name_primary, 'Sibelius Academy')

    def test_institution_set_primary_name_consortium(self):
        inst_parent = Institution.objects.get(id=1)
        inst_parent.set_primary_name()
        inst_parent.save()
        inst_child = Institution.objects.get(id=2)
        inst_child.set_primary_name()
        inst_child.save()
        relationship_type = InstitutionHierarchicalRelationshipType.objects.get(type='consortium')
        InstitutionHierarchicalRelationship.objects.create(
            institution_parent=inst_parent,
            institution_child=inst_child,
            relationship_type=relationship_type
        )
        self.assertEqual(inst_child.name_sort,
                         'University of Applied Sciences of Public Administration, '
                         'Police and Administration of Justice in Güstrow')

    def test_institution_set_primary_name_faculty(self):
        inst_parent = Institution.objects.get(id=1)
        inst_parent.set_primary_name()
        inst_parent.save()
        inst_child = Institution.objects.get(id=3)
        inst_child.set_primary_name()
        inst_child.save()
        relationship_type = InstitutionHierarchicalRelationshipType.objects.get(type='faculty')
        InstitutionHierarchicalRelationship.objects.create(
            institution_parent=inst_parent,
            institution_child=inst_child,
            relationship_type=relationship_type
        )
        self.assertEqual(inst_child.name_sort,
                         'University of applied sciences for Public Administration Rhineland-Palatinate / '
                         'Hessische Hochschule für Polizei und Verwaltung')