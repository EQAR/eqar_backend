from django.test import TestCase

from agencies.models import Agency
from countries.models import Country
from lists.models import QFEHEALevel, Assessment, DegreeOutcome
from programmes.models import ProgrammeName, ProgrammeIdentifier, ProgrammeLearningOutcome
from reports.models import Report
from submissionapi.populators.programme_populator import ProgrammePopulator


class ProgrammePopulatorTestCase(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'degree_outcome',
        'agency_historical_field', 'assessment',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def test_init(self):
        populator = ProgrammePopulator(
            submission={},
            agency=Agency.objects.get(pk=5),
            report=Report.objects.get(pk=1)
        )
        self.assertEqual(populator.agency.acronym_primary, "ACQUIN")
        self.assertEqual(populator.report.local_identifier, "EQARAG0021-EQARIN0001-01")

    def test_create_programme(self):
        populator = ProgrammePopulator(
            submission={
                "countries": [
                    Country.objects.get(iso_3166_alpha2="DE"),
                    Country.objects.get(iso_3166_alpha2="HU")
                ],
                "nqf_level": "level 7",
                "qf_ehea_level": QFEHEALevel.objects.get(code=2)
            },
            agency=Agency.objects.get(pk=5),
            report=Report.objects.get(pk=1)
        )
        populator._create_programme()
        self.assertEqual(populator.programme.report.local_identifier, "EQARAG0021-EQARIN0001-01")
        self.assertEqual(populator.programme.nqf_level, "level 7")
        self.assertEqual(populator.programme.qf_ehea_level.level, "second cycle")

    def test_create_programme_ap(self):
        populator = ProgrammePopulator(
            submission={
                "countries": [
                    Country.objects.get(iso_3166_alpha2="DE"),
                    Country.objects.get(iso_3166_alpha2="HU")
                ],
                "nqf_level": "level 7",
                "qf_ehea_level": QFEHEALevel.objects.get(code=2),
                "degree_outcome": DegreeOutcome.objects.get(id=2),
                "workload_ects": 15,
                "assessment_certification": Assessment.objects.get(pk=3),
                "field_study": "http://data.europa.eu/esco/isced-f/0100",
                "learning_outcome_description": "Learning Outcome Description",
            },
            agency=Agency.objects.get(pk=5),
            report=Report.objects.get(pk=1)
        )
        populator._create_programme()
        self.assertEqual(populator.programme.report.local_identifier, "EQARAG0021-EQARIN0001-01")
        self.assertEqual(populator.programme.degree_outcome_id, 2)
        self.assertEqual(populator.programme.assessment_certification_id, 3)
        self.assertEqual(populator.programme.workload_ects, 15)
        self.assertEqual(populator.programme.field_study, 'http://data.europa.eu/esco/isced-f/0100')
        self.assertEqual(populator.programme.learning_outcome_description, 'Learning Outcome Description')

    def test_programme_name_insert(self):
        populator = ProgrammePopulator(
            submission={
                "name_primary": "Programme Name",
                "qualification_primary": "Qualification Primary",
                "alternative_names": [
                    {
                        "name_alternative": "Alternative Name",
                        "qualification_alternative": "Alternative Qualification"
                    }, {
                        "name_alternative": "Alternative Name 2",
                        "qualification_alternative": "Alternative Qualification 2"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5),
            report=Report.objects.get(pk=1)
        )
        populator._create_programme()
        populator._programme_name_insert()
        programme_name_primary = ProgrammeName.objects.get(programme=populator.programme, name_is_primary=True)
        self.assertEqual(programme_name_primary.name, "Programme Name")
        self.assertEqual(programme_name_primary.qualification, "Qualification Primary")
        self.assertEqual(ProgrammeName.objects.filter(programme=populator.programme).count(), 3)

    def test_programme_identifier_insert(self):
        populator = ProgrammePopulator(
            submission={
                "identifiers": [
                    {
                        "identifier": "Local1122"
                    },
                    {
                        "identifier": "National1122",
                        "resource": "national identifier"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5),
            report=Report.objects.get(pk=1)
        )
        populator._create_programme()
        populator._programme_identifier_insert()
        programme_identifier = ProgrammeIdentifier.objects.filter(programme=populator.programme)
        self.assertEqual(programme_identifier.count(), 2)
        self.assertEqual(programme_identifier.first().resource, "local identifier")
        self.assertEqual(programme_identifier.first().agency.acronym_primary, "ACQUIN")

    def test_programme_learning_outcomes_insert(self):
        populator = ProgrammePopulator(
            submission={
                "learning_outcomes": [
                    'http://data.europa.eu/esco/skill/04a13491-b58c-4d33-8b59-8fad0d55fe9e',
                    'http://data.europa.eu/esco/skill/4ef78abc-e983-4cc7-84a1-52532a0159dc'
                ]
            },
            agency=Agency.objects.get(pk=5),
            report=Report.objects.get(pk=1)
        )
        populator._create_programme()
        populator._programme_learning_outcome_insert()
        programme_learning_outcomes = ProgrammeLearningOutcome.objects.filter(programme=populator.programme)
        self.assertEqual(programme_learning_outcomes.count(), 2)
