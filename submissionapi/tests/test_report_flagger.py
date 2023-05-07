from django.test import TestCase

from agencies.models import AgencyFocusCountry
from countries.models import Country
from institutions.models import InstitutionQFEHEALevel
from lists.models import QFEHEALevel
from reports.models import Report, ReportFlag, ReportStatus
from submissionapi.flaggers.report_flagger import ReportFlagger


class ReportFlaggerTestCase(TestCase):
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
        'programme_demo_13',
        'report_decision', 'report_status',
        'users', 'report_demo_01'
    ]

    def test_init(self):
        flagger = ReportFlagger(
            report=Report.objects.get(pk=1)
        )
        self.assertEqual(flagger.report.agency.acronym_primary, "ACQUIN")

    def test_check_countries(self):
        report = Report.objects.get(pk=1)
        flagger = ReportFlagger(
            report=Report.objects.get(pk=1)
        )
        inst = flagger.report.institutions.create(
            website_link="https://www.kcl.ac.uk/"
        )
        inst.institutioncountry_set.create(
            country=Country.objects.get(iso_3166_alpha2='GB')
        )
        programme = flagger.report.programme_set.create(
            name_primary="Programme",
        )
        programme.countries.add(
            Country.objects.get(iso_3166_alpha2='BG')
        )
        flagger.check_countries()
        flagger.set_flag()
        self.assertEqual(flagger.report.agency.agencyfocuscountry_set.count(), 15)
        self.assertEqual(flagger.report.flag.flag, 'low level')
        report_flags = ReportFlag.objects.filter(report=report)
        self.assertEqual(report_flags.count(), 3, report_flags.count())
        msg = "Institution country [United Kingdom] was not on a list as an Agency Focus country for [ACQUIN]."
        self.assertEqual(report_flags.first().flag_message, msg, report_flags.first().flag_message)

    def test_check_countries_joint_programme_report(self):
        report = Report.objects.get(pk=11)
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
        flagger.check_report_status_country_is_official()
        flagger.set_flag()
        self.assertEqual(flagger.report.flag.flag, 'high level')
        report_flags = ReportFlag.objects.filter(report=report)
        msg = "Report was listed as obligatory, but the Agency (ACQUIN) does not have official status in any of the institution's country"
        self.assertEqual(report_flags.first().flag_message, msg, report_flags.first().flag_message)

    def test_check_programme_qf_ehea_level_voluntary(self):
        report = Report.objects.get(pk=1)
        report.status = ReportStatus.objects.get(pk=2)
        report.save()
        flagger = ReportFlagger(report=report)
        prg = flagger.report.programme_set.first()
        prg.qf_ehea_level = QFEHEALevel.objects.get(pk=4)
        prg.save()
        flagger.check_programme_qf_ehea_level()
        report_flags = ReportFlag.objects.filter(report=report)
        self.assertEqual(report_flags.first().flag.flag, 'high level', report_flags.first().flag.flag)
        msg = "QF-EHEA Level [third cycle] for programme [Verwaltung (B.A.)] " \
              "should be in the institutions QF-EHEA level list."
        self.assertEqual(report_flags.first().flag_message, msg, report_flags.first().flag_message)

    def test_check_programme_qf_ehea_level_voluntary_joint_programme(self):
        report = Report.objects.get(pk=11)
        report.status = ReportStatus.objects.get(pk=2)
        report.save()
        flagger = ReportFlagger(report=report)
        prg = flagger.report.programme_set.first()
        prg.qf_ehea_level = QFEHEALevel.objects.get(pk=4)
        prg.save()
        flagger.check_programme_qf_ehea_level()
        report_flags = ReportFlag.objects.filter(report=report)
        self.assertEqual(report_flags.first().flag.flag, 'high level', report_flags.first().flag.flag)
        msg = "QF-EHEA Level [third cycle] for programme [Public Management] " \
              "should be in the institutions QF-EHEA level list."
        self.assertEqual(report_flags.first().flag_message, msg, report_flags.first().flag_message)

    def test_check_programme_qf_ehea_level_voluntary_joint_programme_ok(self):
        report = Report.objects.get(pk=11)
        report.status = ReportStatus.objects.get(pk=2)
        report.save()
        flagger = ReportFlagger(report=report)
        inst = flagger.report.institutions.first()
        InstitutionQFEHEALevel.objects.create(
            institution=inst,
            qf_ehea_level=QFEHEALevel.objects.get(pk=4),
            qf_ehea_level_verified=True
        )
        prg = flagger.report.programme_set.first()
        prg.qf_ehea_level = QFEHEALevel.objects.get(pk=4)
        prg.save()
        flagger.check_programme_qf_ehea_level()
        flagger.set_flag()
        self.assertEqual(report.flag.flag, 'none', report.flag.flag)

    def test_check_programme_qf_ehea_level_official_joint_programme(self):
        report = Report.objects.get(pk=11)
        flagger = ReportFlagger(report=report)
        prg = flagger.report.programme_set.first()
        prg.qf_ehea_level = QFEHEALevel.objects.get(pk=4)
        prg.save()
        flagger.check_programme_qf_ehea_level()
        report_flags = ReportFlag.objects.filter(report=report)
        self.assertEqual(report_flags.first().flag.flag, 'low level', report_flags.first().flag.flag)
        msg = 'QF-EHEA Level [third cycle] was added to the institution ' \
              '[Fachhochschule für öffentliche Verwaltung, Rechtspflege und Polizei Güstrow]'
        self.assertEqual(report_flags.first().flag_message, msg, report_flags.first().flag_message)

    def test_check_ehea_is_member(self):
        report = Report.objects.get(pk=1)
        flagger = ReportFlagger(
            report=Report.objects.get(pk=1)
        )
        inst = flagger.report.institutions.first()
        inst.set_primary_name()
        inst.save()
        ic = inst.institutioncountry_set.first()
        ic.country.ehea_is_member = True
        ic.country.save()
        inst.institutionqfehealevel_set.all().delete()
        flagger.check_ehea_is_member()
        flagger.set_flag()
        report_flags = ReportFlag.objects.filter(report=report)
        self.assertEqual(report_flags.first().flag.flag, 'low level', report_flags.first().flag.flag)
        msg = "A record was created/identified for an institution " \
              "(University of applied sciences for Public Administration Rhineland-Palatinate) in an " \
              "EHEA member country (Germany) without including QF-EHEA levels."
        self.assertEqual(report_flags.first().flag_message, msg, report_flags.first().flag_message)

    def test_check_report_file(self):
        flagger = ReportFlagger(
            report=Report.objects.get(pk=1)
        )
        flagger.report.reportfile_set.create(
            file_display_name="Test File"
        )
        flagger.check_report_file()
        flagger.set_flag()
        self.assertEqual(flagger.report.flag.flag, 'low level')
