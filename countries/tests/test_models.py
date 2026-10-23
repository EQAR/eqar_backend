import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from agencies.models import AgencyActivityGroup
from countries.models import Country, CountryQARequirementGroup, CountryQARequirement, CountryQAARegulation, \
    CountryInstitutionType


class CountryTestCase(TestCase):
    """
    Test module for the Country class.
    """
    fixtures = [
        'flag',
        'permission_type',
        'country',
    ]

    def test_country_str(self):
        country = Country.objects.get(id=1)
        self.assertEqual(str(country), 'Afghanistan')


class CountryQARequirementTestCase(TestCase):
    """
    Test module for QA requirements groups and QA requirements.
    """
    fixtures = [
        'flag',
        'permission_type',
        'country',
        'agency_activity_type',
        'qf_ehea_level',
        'country_qa_lists',
    ]

    def setUp(self):
        self.country = Country.objects.get(iso_3166_alpha2='DE')
        self.group = CountryQARequirementGroup.objects.create(country=self.country)
        self.programme_activity = AgencyActivityGroup.objects.create(activity='Programme accreditation',
                                                                     activity_type_id=1)
        self.institutional_activity = AgencyActivityGroup.objects.create(activity='Institutional audit',
                                                                         activity_type_id=2)

    def new_requirement(self, **kwargs):
        defaults = {
            'group': self.group,
            'activity_group': self.programme_activity,
            'cbqa_possible_id': 1,
            'cbqa_criteria_id': 1,
            'cbqa_recognition_id': 1,
            'ea_possible_id': 1,
        }
        defaults.update(kwargs)
        return CountryQARequirement(**defaults)

    def assertCleanErrors(self, requirement, fields):
        with self.assertRaises(ValidationError) as cm:
            requirement.clean()
        self.assertEqual(set(cm.exception.message_dict.keys()), set(fields))

    def test_group_str(self):
        self.assertEqual(str(self.group), f'QA requirements group #{self.group.pk}')
        self.group.institution_types.add(CountryInstitutionType.objects.create(country=self.country,
                                                                               name_national='Universität',
                                                                               name_english='University'))
        self.assertEqual(str(self.group), 'University (Universität)')

    def test_group_default_combination_logic(self):
        self.assertEqual(self.group.combination_logic, 'AND')

    def test_requirement_valid(self):
        requirement = self.new_requirement(fields_of_education=['0321'])
        requirement.clean()
        requirement.save()
        self.assertEqual(requirement.country, self.country)

    def test_fields_of_education_normalised(self):
        requirement = self.new_requirement(fields_of_education=[' 0321', 'http://data.europa.eu/esco/isced-f/0321',
                                                                'http://data.europa.eu/esco/isced-f/07'])
        requirement.clean()
        self.assertEqual(requirement.fields_of_education, ['http://data.europa.eu/esco/isced-f/0321',
                                                           'http://data.europa.eu/esco/isced-f/07'])

    def test_fields_of_education_invalid(self):
        self.assertCleanErrors(self.new_requirement(fields_of_education=['12345', 'engineering']),
                               ['fields_of_education'])

    def test_programme_requires_degrees_or_micro_credentials(self):
        self.assertCleanErrors(self.new_requirement(full_degrees=False, micro_credentials=False),
                               ['micro_credentials'])
        self.new_requirement(full_degrees=False, micro_credentials=True).clean()

    def test_institutional_has_no_programme_scope(self):
        self.new_requirement(activity_group=self.institutional_activity, ea_possible_id=None,
                             full_degrees=False, micro_credentials=False).clean()
        self.assertCleanErrors(self.new_requirement(activity_group=self.institutional_activity,
                                                    fields_of_education=['0321'], ea_note='possible'),
                               ['fields_of_education', 'ea_possible', 'ea_note'])

    def test_validity_dates(self):
        self.assertCleanErrors(self.new_requirement(requirement_valid_from=datetime.date(2020, 1, 1),
                                                    requirement_valid_to=datetime.date(2019, 1, 1)),
                               ['requirement_valid_to'])

    def test_new_requirement_mandatory_fields(self):
        self.assertCleanErrors(CountryQARequirement(group=self.group), ['activity_group', 'cbqa_possible'])
        self.assertCleanErrors(self.new_requirement(ea_possible_id=None), ['ea_possible'])

    def test_cbqa_details_only_required_if_possible(self):
        # 'Allowed for all cases'
        self.assertCleanErrors(self.new_requirement(cbqa_possible_id=3, cbqa_criteria_id=None,
                                                    cbqa_recognition_id=None),
                               ['cbqa_criteria', 'cbqa_recognition'])
        # 'Not possible': optional, but not rejected if filled in
        self.new_requirement(cbqa_possible_id=1, cbqa_criteria_id=None, cbqa_recognition_id=None).clean()
        self.new_requirement(cbqa_possible_id=1, cbqa_criteria_id=2, cbqa_recognition_id=None).clean()

    def test_legacy_requirement_may_be_incomplete(self):
        requirement = CountryQARequirement.objects.create(group=self.group, qa_requirement_note='Legacy accreditation')
        requirement.clean()

    def test_regulation_country_from_group(self):
        regulation = CountryQAARegulation(country=Country.objects.get(iso_3166_alpha2='AT'), group=self.group,
                                          regulation='Higher Education Act')
        regulation.save()
        self.assertEqual(regulation.country, self.country)
