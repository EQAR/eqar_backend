from django.test import TestCase

from agencies.models import Agency
from countries.models import Country
from institutions.models import InstitutionName
from lists.models import QFEHEALevel
from submissionapi.populators.institution_populator import InstitutionPopulator


class InstitutionPopulatorTestCase(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'programme_demo_01', 'programme_demo_02', 'programme_demo_03',
        'programme_demo_04', 'programme_demo_05', 'programme_demo_06',
        'programme_demo_07', 'programme_demo_08', 'programme_demo_09',
        'programme_demo_10', 'programme_demo_11', 'programme_demo_12',
        'report_decision', 'report_status',
        'report_demo_01'
    ]

    def test_init(self):
        populator = InstitutionPopulator(
            submission={},
            agency=Agency.objects.get(pk=5),
        )
        self.assertEqual(populator.agency.acronym_primary, "ACQUIN")

    def test_get_institution_if_exists_deqar_id(self):
        populator = InstitutionPopulator(
            submission={"deqar_id": "EQARIN0001"},
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.website_link, "www.hoev-rlp.de")

    def test_get_institution_if_exists_eter_id(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "eter_id": "DE0394"
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.website_link, "http://www.fh-guestrow.de")

    def test_get_institution_if_exists_identifiers(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "identifiers": [
                    {
                        "identifier": "LOCAL001"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.website_link, "www.hoev-rlp.de")

    def test_get_institution_if_exists_identifiers_other(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "identifiers": [
                    {
                        "identifier": "DE0001",
                        "resource": "national identifier"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.website_link, "www.hoev-rlp.de")

    def test_get_institution_if_exists_website_link(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "website": "www.hoev-rlp.de"
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.website_link, "www.hoev-rlp.de")

    def test_get_institution_if_exists_name_official(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "name_official": "Hochschule für öffentliche Verwaltung Rheinland-Pfalz"
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.website_link, "www.hoev-rlp.de")

    def test_get_institution_if_exists_name_english(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "name_english": "University of applied sciences for Public Administration Rhineland-Palatinate"
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.website_link, "www.hoev-rlp.de")

    def test_get_institution_if_eter_exists_website(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "website": "www.fhr-nord.niedersachsen.de"
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.name_primary, 'North German College for Rights, Hildesheim')
        self.assertEqual(populator.institution.institutionqfehealevel_set.count(), 1)

    def test_get_institution_if_eter_exists_name_official(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "name_official": "Norddeutsche Hochschule für Rechtspflege, Hildesheim"
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.name_primary, 'North German College for Rights, Hildesheim')

    def test_get_institution_if_eter_exists_name_english(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN9999",
                "name_english": "North German College for Rights, Hildesheim"
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.name_primary, 'North German College for Rights, Hildesheim')

    def test_institution_create(self):
        populator = InstitutionPopulator(
            submission={
                "name_english": "New University",
                "name_official": "Új egyetem",
                "website": "http://www.new.uni",
                "identifiers": [
                    {
                        "identifier": "LOCAL005"
                    }
                ],
                "alternative_names": [
                    {
                        "name_alternative": "New Alternative University"
                    }
                ],
                "locations": [
                    {
                        "country": Country.objects.get(iso_3166_alpha2="HU"),
                        "city": "Budapest"
                    }
                ],
                "qf_ehea_levels": [
                    QFEHEALevel.objects.get(level="first cycle"), QFEHEALevel.objects.get(level="second cycle")
                ]
            },
            agency=Agency.objects.get(pk=5),
        )
        populator._get_institution_if_exists()
        populator._institution_create()
        self.assertIsNotNone(populator.institution)
        self.assertEqual(populator.institution.name_primary, "New University")
        self.assertEqual(populator.institution.institutionidentifier_set.first().resource, "local identifier")
        self.assertEqual(populator.institution.institutionname_set.first().name_source_note,
                         "Name information supplied by [ACQUIN].")

    def test_institution_existing_populate_identifiers_local_existing(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0001",
                "identifiers": [
                    {
                        "identifier": "LOCAL002",
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_identifiers()
        self.assertEqual(populator.institution.institutionidentifier_set.count(), 2)
        self.assertEqual(populator.institution.institutionidentifier_set.first().identifier, "LOCAL001")

    def test_institution_existing_populate_identifiers_local_existing_other(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0001",
                "identifiers": [
                    {
                        "identifier": "DE0002",
                        "resource": "national identifier"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_identifiers()
        self.assertEqual(populator.institution.institutionidentifier_set.count(), 2)
        self.assertEqual(populator.institution.institutionidentifier_set.first().identifier, "LOCAL001")

    def test_institution_existing_populate_identifiers_local_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0002",
                "identifiers": [
                    {
                        "identifier": "LOCAL001",
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_identifiers()
        self.assertEqual(populator.institution.institutionidentifier_set.count(), 1)
        self.assertEqual(populator.institution.institutionidentifier_set.first().identifier, "LOCAL001")

    def test_institution_existing_populate_identifiers_not_local_existing(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0001",
                "identifiers": [
                    {
                        "identifier": "DE0003",
                        "resource": "national identifier"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_identifiers()
        self.assertEqual(populator.institution.institutionidentifier_set.count(), 2)
        self.assertEqual(populator.institution.institutionidentifier_set.all()[1].identifier, "DE0001")

    def test_institution_existing_populate_identifiers_not_local_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0002",
                "identifiers": [
                    {
                        "identifier": "DE0001",
                        "resource": "national identifier"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_identifiers()
        self.assertEqual(populator.institution.institutionidentifier_set.count(), 1)
        self.assertEqual(populator.institution.institutionidentifier_set.first().identifier, "DE0001")

    def test_institution_existing_populate_name_english_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "name_english": "University of Applied Sciences for Police and Public Administration"
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_name_english()
        self.assertEqual(populator.institution.institutionname_set.count(), 2)
        self.assertEqual(populator.institution.institutionname_set.first().name_english,
                         "University of Applied Sciences for Police and Public Administration")

    def test_institution_existing_populate_name_english_existing(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0001",
                "name_english": "New suggested english title"
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_name_english()
        inst_name = InstitutionName.objects.get(institution=populator.institution)
        self.assertEqual(inst_name.institutionnameversion_set.count(), 1)
        self.assertEqual(inst_name.institutionnameversion_set.first().name,
                         "New suggested english title")

    def test_institution_existing_populate_acronym_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0002",
                "acronym": "FHöVPR"
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_acronym()
        self.assertEqual(populator.institution.institutionname_set.count(), 1)
        self.assertEqual(populator.institution.institutionname_set.first().acronym,
                         "FHöVPR")

    def test_institution_existing_populate_acronym_existing(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "acronym": "HfPV2"
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_acronym()
        self.assertEqual(populator.institution.institutionname_set.count(), 2)
        self.assertTrue(len(populator.institution.institutionname_set.first().name_source_note) > 10)

    def test_institution_existing_populate_name_official_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0002",
                "name_official": "New suggested name official"
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_name_official()
        inst_name = InstitutionName.objects.get(institution=populator.institution)
        self.assertEqual(inst_name.institutionnameversion_set.first().name, "New suggested name official")

    def test_institution_existing_populate_name_official_existing(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "name_official": "Hessische Highschool"
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_name_official()
        inst_name = InstitutionName.objects.filter(institution=populator.institution).first()
        self.assertTrue(len(inst_name.name_source_note) > 10)

    def test_institution_existing_populate_alternative_names_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "alternative_names": [
                    {
                        "name_alternative": "Hessische Highschool Alternative"
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_alternative_names()
        inst_name = InstitutionName.objects.filter(institution=populator.institution).first()
        self.assertEqual(inst_name.institutionnameversion_set.count(), 2)
        self.assertEqual(inst_name.institutionnameversion_set.all()[0].name, "Hessische Highschool Alternative")
        self.assertTrue(len(inst_name.institutionnameversion_set.all()[0].name_version_source_note) > 10)

    def test_institution_existing_populate_locations_country_city_exists_lat_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "locations": [
                    {
                        "country": Country.objects.get(pk=10),
                        "city": "Vienna",
                        "latitude": 9.5000,
                        "longitude": 10.5000
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_locations()
        self.assertEqual(populator.institution.institutioncountry_set.count(), 4)
        self.assertEqual(populator.institution.institutioncountry_set.all()[1].lat, 9.500)

    def test_institution_existing_populate_locations_country_city_exists_city_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "locations": [
                    {
                        "country": Country.objects.get(pk=10),
                        "city": "Salzburg",
                        "latitude": 9.5000,
                        "longitude": 10.5000
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_locations()
        self.assertEqual(populator.institution.institutioncountry_set.count(), 4)
        self.assertTrue(len(populator.institution.institutioncountry_set.all()[1].country_source_note) > 10)

    def test_institution_existing_populate_locations_country_exists_city_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "locations": [
                    {
                        "country": Country.objects.get(pk=74),
                        "city": "Budapest",
                        "latitude": 9.5000,
                        "longitude": 10.5000
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_locations()
        self.assertEqual(populator.institution.institutioncountry_set.count(), 4)
        self.assertEqual(populator.institution.institutioncountry_set.all()[0].city, "Budapest")

    def test_institution_existing_populate_locations_country_new(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "locations": [
                    {
                        "country": Country.objects.get(pk=56),
                        "city": "Tallin",
                        "latitude": 9.5000,
                        "longitude": 10.5000
                    }
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_locations()
        self.assertEqual(populator.institution.institutioncountry_set.count(), 5)
        self.assertEqual(populator.institution.institutioncountry_set.all()[0].city, "Tallin")

    def test_institution_existing_populate_qf_ehea_level(self):
        populator = InstitutionPopulator(
            submission={
                "deqar_id": "EQARIN0003",
                "qf_ehea_levels": [
                    QFEHEALevel.objects.get(pk=4),
                ]
            },
            agency=Agency.objects.get(pk=5)
        )
        populator._get_institution_if_exists()
        populator._institution_existing_populate_qf_ehea_level()
        self.assertEqual(populator.institution.institutionqfehealevel_set.count(), 3)
