from datetime import datetime

from babel.localedata import locale_identifiers
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField

from adminapi.fields import PDFBase64File
from agencies.models import AgencyESGActivity
from submissionapi.serializer_fields.degree_outcome_field import DegreeOutcomeField
from submissionapi.serializer_fields.esco_serializer_field import ESCOSerializer
from submissionapi.serializer_fields.isced_serializer_field import ISCEDSerializer
from institutions.models import Institution, InstitutionIdentifier
from submissionapi.serializer_fields.agency_field import AgencyField
from submissionapi.serializer_fields.assessment_field import AssessmentField
from submissionapi.serializer_fields.contributing_agency_field import ContributingAgencyField
from submissionapi.serializer_fields.country_field import CountryField
from submissionapi.serializer_fields.qf_ehea_level_field import QFEHEALevelField
from submissionapi.serializer_fields.report_decision_field import ReportDecisionField
from submissionapi.serializer_fields.report_identifier_field import ReportIdentifierField
from submissionapi.serializer_fields.report_language_field import ReportLanguageField
from submissionapi.serializer_fields.report_status_field import ReportStatusField
from submissionapi.validations.validate_identifiers_and_resource import validate_identifiers_and_resource
from submissionapi.validations.validate_programmes import validate_programmes
from submissionapi.validations.validate_submission_package_root import validate_submission_package_root


class IdentifierSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=50, required=True,
                                       label='An identifier used by the Agency to identify each institution/programme.',
                                       help_text='example: HCERES21')
    resource = serializers.CharField(max_length=200, required=False,
                                     label='If the identifer is from another source, the source should be recorded as '
                                           'well. If no source is recorded, the source will be recorded as the '
                                           'Agency itself.',
                                     help_text='example: national authority')

    class Meta:
        ref_name = "IdentifierV2Serializer"

class InstitutionAlternativeNameSerializer(serializers.Serializer):
    name_alternative = serializers.CharField(max_length=200, required=True,
                                             label='Alternative name(s) or alternative language name(s) of each '
                                                   'institution in the original alphabet')
    name_alternative_transliterated = serializers.CharField(max_length=200, required=False,
                                                            label='Alternative name(s) or alternative language name(s) '
                                                                  'of each institution in a transliterated form')

    class Meta:
        ref_name = "InstitutionAlternativeNameV2Serializer"

class InstitutionLocatonSerializer(serializers.Serializer):
    country = CountryField(required=True,
                           label='The country where each institution is located, submitted in the form of an '
                                 'ISO 3166 alpha2 or ISO 3166 alpha3 country code.',
                           help_text='examples: "BG", "BGR"')
    city = serializers.CharField(max_length=100, required=False,
                                 label='The city name, preferrably in English, where the institution is located '
                                       'in each country.',
                                 help_text='example: Sofia')
    latitude = serializers.FloatField(required=False,
                                      label='The exact latitude of the institution in the city or the '
                                            'general latitude and longitude of the city itself.',
                                      help_text='example: 42.698334')
    longitude = serializers.FloatField(required=False,
                                       label='The exact longitude of the institution in the city or the '
                                             'general latitude and longitude of the city itself.',
                                       help_text='example: 23.319941')

    def validate(self, data):
        city = data.get('city', None)
        latitude = data.get('latitude', None)
        longitude = data.get('longitude', None)

        if latitude is not None:
            if longitude is None:
                raise serializers.ValidationError("Please provide latitude together with longitude.")

        if longitude is not None:
            if latitude is None:
                raise serializers.ValidationError("Please provide latitude together with longitude.")

        if (latitude is not None and longitude is not None) and city is None:
            raise serializers.ValidationError("Please provide latitude and longitude together with city data.")

        return data

    class Meta:
        ref_name = "InstitutionLocatonV2Serializer"

class InstitutionSerializer(serializers.Serializer):
    # Reference
    deqar_id = serializers.CharField(max_length=25, required=False, label='DEQAR ID of the institution',
                                     help_text='example: "DEQARINST0066"')
    eter_id = serializers.CharField(max_length=15, required=False, label='ETER ID of the institution',
                                    help_text='example: AT0005')

    # Identification
    identifiers = IdentifierSerializer(many=True, required=False)

    def validate_identifiers(self, value):
        return validate_identifiers_and_resource(value)

    # The new institution populator
    def to_internal_value(self, data):
        data = super(InstitutionSerializer, self).to_internal_value(data)

        deqar_id = data.get('deqar_id', None)
        eter_id = data.get('eter_id', None)
        identifiers = data.get('identifiers', None)

        institution_deqar = None
        institution_eter = None

        # Check if DEQAR ID exists
        if deqar_id is not None:
            try:
                institution_deqar = Institution.objects.get(deqar_id=deqar_id)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid DEQAR ID.")

        # Check if ETER ID exists
        if eter_id is not None:
            try:
                institution_eter = Institution.objects.get(eter_id=eter_id)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid ETER ID.")

        # If both ETER ID and DEQAR ID were submitted they should resolve the same institution
        if institution_deqar is not None and institution_eter is not None:
            if institution_deqar.id != institution_eter.id:
                raise serializers.ValidationError("The provided DEQAR and ETER ID does not match.")

        # At this point we will return the one which was resolved
        if institution_deqar:
            return institution_deqar
        if institution_eter:
            return institution_eter

        # If it still didn't resolve, we will try to query the institution by the submitted identifier
        parent_data = self.parent.parent.initial_data
        agency_field = AgencyField()
        agency = agency_field.to_internal_value(parent_data['agency'])

        institutions = set()
        if identifiers is not None:
            for idf in identifiers:
                identifier = idf.get('identifier', None)
                resource = idf.get('resource', 'local identifier')
                try:
                    if resource == 'local identifier':
                        inst_id = InstitutionIdentifier.objects.get(
                            identifier=identifier,
                            resource=resource,
                            agency=agency
                        )
                        institutions.add(inst_id.institution)
                    else:
                        inst_id = InstitutionIdentifier.objects.get(
                            identifier=identifier,
                            resource=resource
                        )
                        institutions.add(inst_id.institution)
                except ObjectDoesNotExist:
                    pass

            # If more than one institution were identified, raise error
            if len(institutions) > 1:
                raise serializers.ValidationError("The submitted institution identifiers are identifying "
                                                  "more institutions. Please correct them.")
            if len(institutions) == 0:
                raise serializers.ValidationError("This report cannot be linked to an institution. "
                                                  "It is missing either a valid ETER ID, DEQAR ID, or "
                                                  "local identifier.")
            if len(institutions) == 1:
                return list(institutions)[0]

        # If there were no ETER ID, DEQAR ID or local identifier submitted
        else:
            raise serializers.ValidationError("This report cannot be linked to an institution. "
                                              "It is missing either a valid ETER ID, DEQAR ID, or "
                                              "local identifier.")

    class Meta:
        ref_name = "InstitutionV2Serializer"

class ProgrammeAlternativeNameSerializer(serializers.Serializer):
    name_alternative = serializers.CharField(max_length=200, required=True,
                                             label='Any alternative or other language name for a programme.',
                                             help_text='example: Medical Natural Sciences')
    qualification_alternative = serializers.CharField(max_length=200, required=False,
                                                      label='The qualification offered by each programme recorded in '
                                                            'the same language that is used for the alternative '
                                                            'name version.',
                                                      help_text='example: Master of Medicine in de specialistische '
                                                                'geneeskunde')

    class Meta:
        ref_name = "ProgrammeAlternativeNameV2Serializer"

class ProgrammeSerializer(serializers.Serializer):
    # Identification
    identifiers = IdentifierSerializer(many=True, required=False)

    # Name
    name_primary = serializers.CharField(max_length=255, required=True, label='The primary name of each programme.',
                                         help_text='example: Medical Natural Sciences')
    qualification_primary = serializers.CharField(max_length=255, required=False,
                                                  label='The qualification offered by each programme recorded in the '
                                                        'same language that is used for primary name.',
                                                  help_text='example: Master of Medicine in de specialistische '
                                                            'geneeskunde')
    alternative_names = ProgrammeAlternativeNameSerializer(many=True, required=False)

    # Country
    countries = serializers.ListField(child=CountryField(required=False), required=False,
                                      label='The countries where each programme is located, when different from the '
                                            'main country/ies of the institution(s), in the form of an ISO 3166 alpha2 '
                                            'or ISO 3166 alpha3 country code.',
                                      help_text='examples: "BE", "BEL"')

    # Level
    nqf_level = serializers.CharField(max_length=255, required=False,
                                      label='Programme NQF level',
                                      help_text='example: "level 6"')
    qf_ehea_level = QFEHEALevelField(required=True,
                                     label='Prgoramme QF EHEA level',
                                     help_text='accepted values: "0", "1", "2", "3", "short cycle", '
                                               '"first cycle", "second cycle", "third cycle"')

    # Micro Credentials
    degree_outcome = DegreeOutcomeField(required=True,
                                        label='A programme, in combination with other programmes, can lead to a '
                                              'full degree (i.e. of bachelors, master or PhD) or not. This is what '
                                              'distinguishes traditional programmes from micro credentials.',
                                        help_text='accepted values: 1, "1", "yes", "full degree",'
                                                  '2, "2", "no", "no full degree")')
    workload_ects = serializers.IntegerField(required=False,
                                             label='The workload as number of ECTS credits for programmes'
                                                   'that do not lead to a full degree (i.e. micro '
                                                   'credentials) must be provided to indicate the '
                                                   'volume of learning.',
                                             help_text='example: 1, 15')
    learning_outcomes = serializers.ListField(child=ESCOSerializer(
        label='DEQAR uses the the European Skills, Competences, Qualifications '
              'and Occupations (ESCO) classification of skills and competences '
              'as the preferred and interoperable way to specify the learning '
              'outcomes of a programme.',
        help_text='example: "http://data.europa.eu/esco/skill/77f109c4-3107-4d2a-a512-5160ac103933"'),
        required=False)
    learning_outcome_description = serializers.CharField(required=False,
                                                         label="Free text field to describe the programme's learning "
                                                               "outcomes.",
                                                         help_text='example: "The learner acquires planning and '
                                                                   'organizing skills in the Scrum software."')
    field_study = ISCEDSerializer(required=False,
                                  label='DEQAR is using the International Standard Classification of '
                                        'Education (ISCED) framework (2013) for assembling the '
                                        'organisation of education programmes and related '
                                        'qualifications by levels and fields of education.',
                                  help_text='example: "0321", "http://data.europa.eu/esco/isced-f/0321"')
    assessment_certification = AssessmentField(required=False,
                                               label='While a programme does not lead to a full degree, '
                                                     'it could still have a formal outcome.',
                                               help_text='accepted_values: "1", "2", "3", '
                                                         '"Attendance certificate", "Assessment based certificate", '
                                                         '"No assessment and no certificate"')

    def validate_identifiers(self, value):
        return validate_identifiers_and_resource(value)

    def validate(self, data):
        data = super(ProgrammeSerializer, self).validate(data)
        return validate_programmes(data)

    class Meta:
        ref_name = "ProgrammeV2Serializer"

class ReportFileSerializer(serializers.Serializer):
    original_location = serializers.URLField(max_length=500, required=False, label='The URL of the report file',
                                             help_text='example: "http://estudis.aqu.cat/MAD2014_UPC_es.pdf"')
    display_name = serializers.CharField(max_length=255, required=False, label='Display value of the file',
                                         help_text='example: "Ev. de la Solicitud de Verification de Título oficial"')
    report_language = serializers.ListField(child=ReportLanguageField(required=True), required=True,
                                            label='Language(s) of the report',
                                            help_text='example: ["eng", "ger"]')
    file = PDFBase64File(required=False, label='The report file in PDF format encoded with Base64')
    file_name = serializers.CharField(required=False, max_length=255, allow_blank=True,
                                      label='The name of the file, required if you embed the file in the upload request',
                                      help_text='example: ACQUIN_institutional_report.pdf')

    def validate(self, data):
        file = data.get('file', None)
        file_name = data.get('file_name', None)

        original_location = data.get('original_location', None)

        if file:
            if not file_name or file_name == '':
                raise ValidationError("Please provide a file name for the uploaded file.")

            if original_location:
                raise ValidationError("You cannot submit both a file and an original_location URL.")

        return super(ReportFileSerializer, self).validate(data)

    class Meta:
        ref_name = "ReportFileV2Serializer"

class ReportLinkSerializer(serializers.Serializer):
    link = serializers.URLField(max_length=255, required=True,
                                label="Links to the Report records/pages on the Agency's website.",
                                help_text='example: "http://srv.aneca.es/ListadoTitulos/node/1182321350"')
    link_display_name = serializers.CharField(max_length=200, required=False,
                                              label='Display the report records link.',
                                              help_text='example: "General information on programme"')

    class Meta:
        ref_name = "ReportLinkV2Serializer"


class ActivitySerializer(serializers.Serializer):
    activity = serializers.CharField(max_length=500, required=False,
                                     label='Identifier of the Agency ESG Activity',
                                     help_text='examples: "2"')
    local_identifier = serializers.CharField(max_length=200, required=False,
                                             label='Local identifier of the ESG Activity',
                                             help_text='example: "inst_audit')
    agency = AgencyField(required=False, label='Identifier or the acronym of the agency whose local identifier is used. '
                                               'If not provided, the agency of the report will be used.',
                         help_text='examples: "33", "ACQUIN"')

    def to_internal_value(self, data):
        activity = data.get('activity', None)
        local_identifier = data.get('local_identifier', None)
        agency = data.get('agency', None)

        # Get the submitting agency
        parent_data = self.parent.parent.initial_data
        agency_field = AgencyField()
        submitting_agency = agency_field.to_internal_value(parent_data['agency'])

        if activity is None and local_identifier is None:
            raise serializers.ValidationError("Either ESG Activity ID or ESG Activity local identifier is needed.")

        if activity is not None and local_identifier is not None:
            raise serializers.ValidationError("You cannot submit both ESG Activity ID and ESG Activity local identifier.")

        if activity is not None:
            if str(activity).isdigit():
                try:
                    data = AgencyESGActivity.objects.get(pk=activity, agency=submitting_agency)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Please provide valid ESG Activity ID.")
            else:
                raise serializers.ValidationError("Please provide ESG Activity ID as an integer or string.")

        if local_identifier is not None:
            if agency is None:
                try:
                    data = AgencyESGActivity.objects.get(
                        activity_local_identifier=local_identifier, agency=submitting_agency)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Please provide valid ESG Activity local identifier.")
            else:
                try:
                    data = AgencyESGActivity.objects.get(
                        activity_local_identifier=local_identifier, agency=agency)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Please provide valid ESG Activity local identifier with Agency info.")

        return data

    class Meta:
        ref_name = "ActivityV2Serializer"

class SubmissionPackageSerializer(serializers.Serializer):
    # Report Creator
    agency = AgencyField(required=True, label='Identifier or the acronym of the agency',
                         help_text='examples: "33", "ACQUIN"')

    # Report Contributor Agencies
    contributing_agencies = ListField(
        required=False,
        label="List of the contributing agencies",
        child=ContributingAgencyField(label='Identifier or the acronym of the agency',
                                      help_text='examples: "33", "ACQUIN"'),
    )

    # Record Identification
    local_identifier = serializers.CharField(max_length=255, required=False, label='Local identifier of the report',
                                             help_text='example: "QAA1153-March15"')

    # Report Activity
    activities = ActivitySerializer(many=True, required=True)

    # Report Details
    status = ReportStatusField(required=True, label='Identifier or the status of the report',
                               help_text='accepted values: "1", "2", "part of obligatory EQA system", "voluntary"')
    decision = ReportDecisionField(required=True, label='Identifier or the decision described in the report',
                                   help_text='accepted values: "1", "2", "3", "4", "positive", '
                                             '"positive with conditions or restrictions", "no, negative", '
                                             '"not applicable"')
    summary = serializers.CharField(required=False, label="Summary of the report.")

    # Report Validity
    valid_from = serializers.CharField(max_length=20, required=True, label='Starting date of the report validity',
                                       help_text='example: 15-01-2015')
    valid_to = serializers.CharField(max_length=20, required=False, label='End date of the report validity',
                                     help_text='example: 15-01-2015', allow_null=True)
    date_format = serializers.CharField(max_length=20, required=True, label='The date format of the validation dates.',
                                        help_text='example: %d-%M-%Y')

    # Report Links
    report_links = ReportLinkSerializer(many=True, required=False)

    # Report Files
    report_files = ReportFileSerializer(many=True, required=False)

    # Institutions
    institutions = InstitutionSerializer(many=True, required=True,
                                         label='Institution(s) which are the subject of the report. '
                                               '(If programme information is submitted, then the report considered '
                                               'to be about the programme itself.)', allow_empty=False)

    # Programmes
    programmes = ProgrammeSerializer(many=True, required=False,
                                     label='Programme(s) which are the subject of the report. '
                                           '(If programme information is NOT submitted, then the report considered '
                                           'to be about the institution.)')

    # Comment
    other_comment = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                          label='Comment for the submission.')

    def to_internal_value(self, data):
        errors = []
        data = super(SubmissionPackageSerializer, self).to_internal_value(data)

        date_format = data.get('date_format', '%Y-%m-%d')

        valid_from = data.get('valid_from')
        valid_to = data.get('valid_to', None)

        agency = data.get('agency', None)

        #
        # Validate if date format is applicable, default format is %Y-%m-%d.
        # If yes, resolve the date values
        #
        try:
            date_from = datetime.strptime(valid_from, date_format)
            data['valid_from'] = date_from.strftime("%Y-%m-%d")
            if valid_to:
                date_to = datetime.strptime(valid_to, date_format)
                data['valid_to'] = date_to.strftime("%Y-%m-%d")
        except ValueError:
            errors.append("Date format string is not applicable to the submitted date.")

        # If there are errors raise ValidationError
        #
        if len(errors) > 0:
            raise serializers.ValidationError({settings.NON_FIELD_ERRORS_KEY: errors})
        return data

    def validate(self, data):
        data = super(SubmissionPackageSerializer, self).validate(data)
        return validate_submission_package_root(data)

    class Meta:
        ref_name = "SubmissionPackageV2Serializer"

class SubmissionPackageCreateSerializer(SubmissionPackageSerializer):
    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if 'report_id' in unknown:
            raise serializers.ValidationError("You submitted a report_id. To update an existing report, please use a "
                                              "PUT or PATCH request instead of a POST.")
        return super(SubmissionPackageCreateSerializer, self).validate(attrs)

class SubmissionPackageUpdateSerializer(SubmissionPackageSerializer):
    # Report Identifier
    report_id = ReportIdentifierField(required=True, label='DEQAR identifier of the report')