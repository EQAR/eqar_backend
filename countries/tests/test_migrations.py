from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class LegacyQARequirementsMigrationTestCase(TransactionTestCase):
    """
    Tests migrations 0015-0018, which move legacy QA requirements into default QA requirements groups and then drop
    the legacy fields.
    """
    serialized_rollback = True

    legacy_state = [('countries', '0014_delete_countryhistorical')]
    grouped_state = [('countries', '0017_remove_qa_requirement_country')]
    final_state = [('countries', '0018_remove_legacy_qa_fields')]

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def setUp(self):
        call_command('loaddata', 'flag', 'permission_type', 'country_qa_lists', verbosity=0)
        apps = self.migrate(self.legacy_state)

        Country = apps.get_model('countries', 'Country')
        CountryInstitutionType = apps.get_model('countries', 'CountryInstitutionType')
        CountryQARequirement = apps.get_model('countries', 'CountryQARequirement')
        CountryQARequirementType = apps.get_model('countries', 'CountryQARequirementType')

        for pk, title in ((1, 'institutional level'), (2, 'programme level'),
                          (3, 'institutional and programme level')):
            CountryQARequirementType.objects.create(id=pk, qa_requirement_type=title)

        country_defaults = {'flag_id': 1, 'ehea_key_commitment_id': 2}
        self.country_a = Country.objects.create(
            iso_3166_alpha2='AA', name_english='Country A', **country_defaults,
            external_QAA_is_permitted_id=1, european_approach_is_permitted_id=3,
            eligibility='<p>EQAR registration</p>', conditions='<p><br></p>', recognition='by the national agency',
            external_QAA_note='', european_approach_note='<p>only for joint programmes</p>',
        ).id
        self.country_b = Country.objects.create(
            iso_3166_alpha2='BB', name_english='Country B', **country_defaults,
            external_QAA_is_permitted_id=3, european_approach_is_permitted_id=2,
        ).id
        self.country_c = Country.objects.create(iso_3166_alpha2='CC', name_english='Country C',
                                                **country_defaults).id
        self.country_d = Country.objects.create(
            iso_3166_alpha2='DD', name_english='Country D', **country_defaults,
            european_approach_is_permitted_id=1, european_approach_note='self-accrediting institutions',
        ).id

        self.types_a = {
            CountryInstitutionType.objects.create(country_id=self.country_a, name_national='Universität').id,
            CountryInstitutionType.objects.create(country_id=self.country_a, name_national='Fachhochschule').id,
        }
        CountryInstitutionType.objects.create(country_id=self.country_a, name_national='Akademie', is_active=False)

        self.req_a_institutional = CountryQARequirement.objects.create(
            country_id=self.country_a, qa_requirement='Institutional audit', qa_requirement_type_id=1,
            qa_requirement_note='every 6 years').id
        self.req_a_programme = CountryQARequirement.objects.create(
            country_id=self.country_a, qa_requirement='Programme accreditation.', qa_requirement_type_id=2).id
        self.req_b = CountryQARequirement.objects.create(
            country_id=self.country_b, qa_requirement='Accreditation', qa_requirement_type_id=3,
            qa_requirement_note='<p>every 5 years</p>').id
        self.req_d = CountryQARequirement.objects.create(
            country_id=self.country_d, qa_requirement='Institutional audit', qa_requirement_type_id=1).id

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_requirements_grouped(self):
        apps = self.migrate(self.grouped_state)
        CountryQARequirement = apps.get_model('countries', 'CountryQARequirement')
        CountryQARequirementGroup = apps.get_model('countries', 'CountryQARequirementGroup')

        # one default group per country that has requirements
        self.assertEqual(CountryQARequirementGroup.objects.filter(country_id=self.country_a).count(), 1)
        self.assertEqual(CountryQARequirementGroup.objects.filter(country_id=self.country_b).count(), 1)
        self.assertFalse(CountryQARequirementGroup.objects.filter(country_id=self.country_c).exists())

        group_a = CountryQARequirementGroup.objects.get(country_id=self.country_a)
        self.assertEqual(group_a.combination_logic, 'AND')
        self.assertEqual(set(group_a.institution_types.values_list('id', flat=True)), self.types_a)

        institutional = CountryQARequirement.objects.get(id=self.req_a_institutional)
        programme = CountryQARequirement.objects.get(id=self.req_a_programme)
        self.assertEqual(institutional.group_id, group_a.id)
        self.assertEqual(programme.group_id, group_a.id)

        # legacy titles prepended to notes
        self.assertEqual(institutional.qa_requirement_note, 'Institutional audit: every 6 years')
        self.assertEqual(programme.qa_requirement_note, 'Programme accreditation')

        # cross-border QA: permitted -> 'Allowed for all cases', text copied without empty parts
        self.assertEqual(institutional.cbqa_possible_id, 3)
        self.assertEqual(institutional.cbqa_other_requirements_note,
                         '<p><strong>Eligibility:</strong></p>\n<p>EQAR registration</p>\n'
                         '<p><strong>Recognition:</strong></p>\nby the national agency')
        self.assertEqual(programme.cbqa_other_requirements_note, institutional.cbqa_other_requirements_note)

        # European Approach only for programme-level requirements: partially -> 'Yes, subject to conditions'
        self.assertIsNone(institutional.ea_possible_id)
        self.assertEqual(institutional.ea_note, '')
        self.assertEqual(programme.ea_possible_id, 2)
        self.assertEqual(programme.ea_note, '<p>only for joint programmes</p>')

        # partially permitted CBQA cannot be mapped; EA not permitted -> 'No'
        requirement_b = CountryQARequirement.objects.get(id=self.req_b)
        self.assertEqual(requirement_b.group.country_id, self.country_b)
        self.assertEqual(requirement_b.qa_requirement_note, '<p>Accreditation: every 5 years</p>')
        self.assertIsNone(requirement_b.cbqa_possible_id)
        self.assertEqual(requirement_b.cbqa_other_requirements_note, '')
        self.assertEqual(requirement_b.ea_possible_id, 3)

        # country without programme-level requirements: European Approach copied to institutional ones
        requirement_d = CountryQARequirement.objects.get(id=self.req_d)
        self.assertEqual(requirement_d.ea_possible_id, 1)
        self.assertEqual(requirement_d.ea_note, 'self-accrediting institutions')

    def test_legacy_fields_dropped(self):
        apps = self.migrate(self.final_state)
        Country = apps.get_model('countries', 'Country')
        CountryQARequirement = apps.get_model('countries', 'CountryQARequirement')

        for field in ('eligibility', 'conditions', 'recognition', 'external_QAA_note', 'european_approach_note'):
            with self.assertRaises(FieldDoesNotExist):
                Country._meta.get_field(field)
        for field in ('qa_requirement', 'qa_requirement_type'):
            with self.assertRaises(FieldDoesNotExist):
                CountryQARequirement._meta.get_field(field)
        with self.assertRaises(LookupError):
            apps.get_model('countries', 'CountryQARequirementType')

        self.assertEqual(Country.objects.get(id=self.country_a).external_QAA_is_permitted_id, 1)
        self.assertEqual(CountryQARequirement.objects.get(id=self.req_a_institutional).qa_requirement_note,
                         'Institutional audit: every 6 years')

    def test_reversible(self):
        self.migrate(self.grouped_state)
        apps = self.migrate(self.legacy_state)
        CountryQARequirement = apps.get_model('countries', 'CountryQARequirement')

        institutional = CountryQARequirement.objects.get(id=self.req_a_institutional)
        self.assertEqual(institutional.country_id, self.country_a)
        self.assertEqual(institutional.qa_requirement_note, 'every 6 years')
        self.assertEqual(CountryQARequirement.objects.get(id=self.req_a_programme).qa_requirement_note, '')
        self.assertEqual(CountryQARequirement.objects.get(id=self.req_b).country_id, self.country_b)
        self.assertEqual(CountryQARequirement.objects.get(id=self.req_b).qa_requirement_note, '<p>every 5 years</p>')
