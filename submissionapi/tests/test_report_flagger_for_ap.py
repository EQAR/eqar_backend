from django.test import TestCase

from agencies.models import AgencyFocusCountry
from countries.models import Country
from institutions.models import InstitutionQFEHEALevel
from lists.models import QFEHEALevel
from reports.models import Report, ReportFlag, ReportStatus
from submissionapi.flaggers.report_flagger import ReportFlagger


class ReportFlaggerAPTestCase(TestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eter_demo', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'degree_outcome',
        'agency_historical_field',
        'agency_demo_01', 'agency_demo_02', 'association', 'assessment',
        'submitting_agency_demo',
        'institution_historical_field',
        'institution_demo_01',
        'alternative_provider_01', 'alternative_provider_02',
        'programme_demo_ap_01', 'programme_demo_ap_02', 'programme_demo_ap_03',
        'report_decision', 'report_status',
        'users', 'report_demo_ap_01'
    ]

    def test_init(self):
        flagger = ReportFlagger(
            report=Report.objects.get(pk=13)
        )
        self.assertEqual(flagger.report.agency.acronym_primary, "ACQUIN")

    def test_report_status_country_is_official_for_multi_institution_ap_only(self):
        report = Report.objects.get(pk=12)
        flagger = ReportFlagger(
            report=report
        )
        inst = flagger.report.institutions.create(
            website_link="https://www.kcl.ac.uk/"
        )
        inst.institutioncountry_set.create(
            country=Country.objects.get(iso_3166_alpha2='GB')
        )
        agency_focus_country = AgencyFocusCountry.objects.get(
            agency=report.agency,
            country__id=64
        )
        agency_focus_country.country_is_official = False
        agency_focus_country.save()
        flagger.check_report_status_country_is_official_for_multi_institution()
        flagger.set_flag()
        self.assertEqual(flagger.report.flag.flag, 'none')


    def test_report_status_country_is_official_for_multi_institution_ap_mixed(self):
        report = Report.objects.get(pk=13)
        flagger = ReportFlagger(
            report=report
        )
        inst = flagger.report.institutions.create(
            website_link="https://www.kcl.ac.uk/"
        )
        inst.institutioncountry_set.create(
            country=Country.objects.get(iso_3166_alpha2='GB')
        )
        agency_focus_country = AgencyFocusCountry.objects.get(
            agency=report.agency,
            country__id=64
        )
        agency_focus_country.country_is_official = False
        agency_focus_country.save()
        flagger.check_report_status_country_is_official_for_multi_institution()
        flagger.set_flag()
        self.assertEqual(flagger.report.flag.flag, 'high level')

    def test_check_programme_qf_ehea_level_for_multi_institutions_ap_only(self):
        report = Report.objects.get(pk=12)
        prg = report.programme_set.first()
        prg.qf_ehea_level = QFEHEALevel.objects.get(pk=4)
        prg.save()
        flagger = ReportFlagger(
            report=report
        )
        flagger.check_programme_qf_ehea_level()
        flagger.set_flag()
        self.assertEqual(flagger.report.flag.flag, 'none')
        self.assertTrue(InstitutionQFEHEALevel.objects.filter(
            institution=10,
            qf_ehea_level_id=4
        ).exists())
        self.assertTrue(InstitutionQFEHEALevel.objects.filter(
            institution=11,
            qf_ehea_level_id=4
        ).exists())
