from django.contrib.auth.models import User
from django.test import RequestFactory
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from accounts.models import DEQARProfile
from agencies.models import SubmittingAgency
from submissionapi.serializer_fields.agency_field import AgencyField
from submissionapi.serializer_fields.assessment_field import AssessmentField
from submissionapi.serializer_fields.contributing_agency_field import ContributingAgencyField
from submissionapi.serializer_fields.country_field import CountryField
from submissionapi.serializer_fields.degree_outcome_field import DegreeOutcomeField
from submissionapi.serializer_fields.qf_ehea_level_field import QFEHEALevelField
from submissionapi.serializer_fields.report_decision_field import ReportDecisionField
from submissionapi.serializer_fields.report_identifier_field import ReportIdentifierField
from submissionapi.serializer_fields.report_language_field import ReportLanguageField
from submissionapi.serializer_fields.report_status_field import ReportStatusField


class SerializerFieldValidationTestCase(APITestCase):
    fixtures = [
        'country_qa_requirement_type', 'country', 'qf_ehea_level', 'eqar_decision_type', 'language',
        'agency_activity_type', 'agency_focus', 'identifier_resource', 'flag', 'permission_type', 'assessment',
        'agency_historical_field', 'degree_outcome',
        'agency_demo_01', 'agency_demo_02', 'association',
        'submitting_agency_demo',
        'institution_historical_field',
        'institution_demo_01', 'institution_demo_02', 'institution_demo_03',
        'report_status', 'report_decision', 'users', 'report_demo_01'
    ]

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='testuser',
            email='testuser@eqar.eu',
            password='testpassword'
        )
        self.profile = DEQARProfile.objects.create(
            user=self.user,
            submitting_agency=SubmittingAgency.objects.get(pk=1)
        )
        self.user.save()

        factory = RequestFactory()
        self.request = factory.post('/submissionapi/v1/submit/report')
        self.request.user = self.user

    # AgencyField tests
    def test_agency_field_not_string(self):
        field = AgencyField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_agency_deqar_id_ok(self):
        pass

    def test_agency_deqar_id_error(self):
        field = AgencyField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Agency DEQAR ID.'):
            field.to_internal_value("999")

    def test_agency_acronym_ok(self):
        pass

    def test_agency_acronym_error(self):
        field = AgencyField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Agency Acronym.'):
            field.to_internal_value("ECQUIN")

    # Assessment tests
    def test_assessment_field_not_string(self):
        field = AssessmentField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_assessment_id_ok(self):
        field = AssessmentField()
        value = field.to_internal_value("1")
        self.assertEqual(value.assessment, "Attendance certificate")

    def test_assessment_id_error(self):
        field = AssessmentField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Assessment ID.'):
            field.to_internal_value("999")

    def test_assessment_str_ok(self):
        field = AssessmentField()
        value = field.to_internal_value("Assessment based certificate")
        self.assertEqual(value.assessment, "Assessment based certificate")

    def test_assessment_str_error(self):
        field = AssessmentField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid assessment name.'):
            field.to_internal_value("not a good assessment value")

    # ContributingAgency tests
    def test_contributing_agency_field_not_string(self):
        field = ContributingAgencyField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_contributing_agency_deqar_id_ok(self):
        pass

    def test__contributing_agency_deqar_id_error(self):
        field = ContributingAgencyField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Agency DEQAR ID.'):
            field.to_internal_value("999")

    def test__contributing_agency_acronym_ok(self):
        pass

    def test__contributing_agency_acronym_error(self):
        field = ContributingAgencyField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Agency Acronym.'):
            field.to_internal_value("ECQUIN")

    # ReportStatusField tests
    def test_report_status_field_not_string(self):
        field = ReportStatusField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_report_status_id_ok(self):
        field = ReportStatusField()
        value = field.to_internal_value("1")
        self.assertEqual(value.status, "part of obligatory EQA system")

    def test_report_status_id_error(self):
        field = ReportStatusField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Report Status ID.'):
            field.to_internal_value("999")

    def test_report_status_str_ok(self):
        field = ReportStatusField()
        value = field.to_internal_value("voluntary")
        self.assertEqual(value.status, "voluntary")

    def test_report_status_str_error(self):
        field = ReportStatusField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Report Status.'):
            field.to_internal_value("part of obligatory EQA system wrong string")

    # ReportDecisionField tests
    def test_report_decision_field_not_string(self):
        field = ReportDecisionField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_report_decision_id_ok(self):
        field = ReportDecisionField()
        value = field.to_internal_value("1")
        self.assertEqual(value.decision, "positive")

    def test_report_decision_id_error(self):
        field = ReportDecisionField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Report Decision ID.'):
            field.to_internal_value("999")

    def test_report_decision_str_ok(self):
        field = ReportDecisionField()
        value = field.to_internal_value("positive")
        self.assertEqual(value.decision, "positive")

    def test_report_decision_str_error(self):
        field = ReportDecisionField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Report Decision.'):
            field.to_internal_value("almost positive :)")

    # ReportLanguageField tests
    def test_report_language_field_not_string(self):
        field = ReportLanguageField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_report_language_iso639_1_ok(self):
        field = ReportLanguageField()
        value = field.to_internal_value("de")
        self.assertEqual(value.language_name_en, "German")

    def test_report_language_iso639_1_error(self):
        field = ReportLanguageField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid language code.'):
            field.to_internal_value("xx")

    def test_report_language_iso639_2_ok(self):
        field = ReportLanguageField()
        value = field.to_internal_value("ger")
        self.assertEqual(value.language_name_en, "German")

    def test_report_language_iso639_2_error(self):
        field = ReportLanguageField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid language code.'):
            field.to_internal_value("xxx")

    def test_report_language_error(self):
        field = ReportLanguageField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid language code.'):
            field.to_internal_value("x")

    # QFEHEALevelField tests
    def test_qf_ehea_level_field_not_string(self):
        field = QFEHEALevelField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_qf_ehea_level_id_ok(self):
        field = QFEHEALevelField()
        value = field.to_internal_value("0")
        self.assertEqual(value.level, "short cycle")

    def test_qf_ehea_level_id_error(self):
        field = QFEHEALevelField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid QF EHEA ID.'):
            field.to_internal_value("999")

    def test_qf_ehea_level_str_ok(self):
        field = QFEHEALevelField()
        value = field.to_internal_value("short cycle")
        self.assertEqual(value.level, "short cycle")

    def test_qf_ehea_level_str_error(self):
        field = QFEHEALevelField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid QF EHEA level.'):
            field.to_internal_value("shortest cycle :)")

    # CountryField tests
    def test_country_not_string(self):
        field = CountryField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_country_alpha2_ok(self):
        field = CountryField()
        value = field.to_internal_value("de")
        self.assertEqual(value.name_english, "Germany")

    def test_country_alpha2_error(self):
        field = CountryField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid country code.'):
            field.to_internal_value("xx")

    def test_country_alpha3_ok(self):
        field = CountryField()
        value = field.to_internal_value("deu")
        self.assertEqual(value.name_english, "Germany")

    def test_country_alpha3_error(self):
        field = CountryField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid country code.'):
            field.to_internal_value("xxx")

    def test_country_error(self):
        field = CountryField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid country code.'):
            field.to_internal_value("x")

    # Report Identifier tests
    def test_report_identifier_not_string(self):
        field = ReportIdentifierField()
        with self.assertRaisesRegex(ValidationError, 'Incorrect type.'):
            field.to_internal_value(1)

    def test_report_identifier_valid(self):
        pass

    def test_report_identifier_invalid(self):
        field = ReportIdentifierField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid Report ID.'):
            field.to_internal_value("999")

    def test_degree_outcome_ok(self):
        field = DegreeOutcomeField()
        value = field.to_internal_value("1")
        self.assertEqual(value.outcome, "Full degree")
        value = field.to_internal_value("no")
        self.assertEqual(value.outcome, "No full degree")


    def test_degree_outcome_invalid(self):
        field = DegreeOutcomeField()
        with self.assertRaisesRegex(ValidationError, 'Please provide valid degree_outcome value.'):
            field.to_internal_value("TRUE")
