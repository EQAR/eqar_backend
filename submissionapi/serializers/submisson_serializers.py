from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from agencies.models import AgencyESGActivity
from institutions.models import Institution, InstitutionETERRecord, InstitutionIdentifier
from reports.models import Report
from submissionapi.fields import AgencyField, ReportStatusField, ReportDecisionField, ReportLanguageField, \
    QFEHEALevelField, CountryField, ReportIdentifierField


class IdentifierSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=50, required=True,
                                       label='An identifier used by the Agency to identify each institution/programme.',
                                       help_text='example: HCERES21')
    resource = serializers.CharField(max_length=200, required=False,
                                     label='If the identifer is from another source, the source should be recorded as '
                                           'well. If no source is recorded, the source will be recorded as the '
                                           'Agency itself.',
                                     help_text='example: national authority')


class InstitutionAlternativeNameSerializer(serializers.Serializer):
    name_alternative = serializers.CharField(max_length=200, required=True,
                                             label='Alternative name(s) or alternative language name(s) of each '
                                                   'institution in the original alphabet')
    name_alternative_transliterated = serializers.CharField(max_length=200, required=False,
                                                            label='Alternative name(s) or alternative language name(s) '
                                                                  'of each institution in a transliterated form')


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


class InstitutionSerializer(serializers.Serializer):
    # Reference
    deqar_id = serializers.CharField(max_length=25, required=False, label='DEQAR ID of the institution',
                                     help_text='example: "EQARInst66"')
    eter_id = serializers.CharField(max_length=15, required=False, label='ETER ID of the institution',
                                    help_text='example: AT0005')

    # Identification
    identifiers = IdentifierSerializer(many=True, required=False)

    # Name
    name_official = serializers.CharField(max_length=255, required=False,
                                          label='The official form of the name of the institution',
                                          help_text='example: Югозападен университет Неофит Рилски')
    name_official_transliterated = serializers.CharField(max_length=255, required=False,
                                                         label='The english form of the name of the institution',
                                                         help_text='example: Yugo-zapaden universitet Neofit Rilski')
    name_english = serializers.CharField(max_length=255, required=False,
                                         label='The english form of the name of the institution',
                                         help_text='example: Yugo-zapaden universitet Neofit Rilski')
    acronym = serializers.CharField(max_length=30, required=False,
                                    label='The official form of the acronym of the institution',
                                    help_text='example: SWU')
    alternative_names = InstitutionAlternativeNameSerializer(many=True, required=False)

    # Location
    locations = InstitutionLocatonSerializer(many=True, required=False,
                                             label='List of locations where the institution is located')

    # Level
    qf_ehea_levels = serializers.ListField(child=QFEHEALevelField(required=False), required=False,
                                           label='List of identifiers or QF-EHEA levels that are valid for '
                                                 'each institution',
                                           help_text='accepted values: "0", "1", "2", "3", "short cycle", '
                                                     '"first cycle", "second cycle", "third cycle"')

    # Website
    website_link = serializers.URLField(max_length=200, required=False, label='Website of the institution.',
                                        help_text='example: https://www.tuwien.ac.at')

    def validate_identifiers(self, value):
        # Validate if there is only one identifier without resource id
        count = 0
        resources = []
        for identifier in value:
            if 'resource' not in identifier.keys():
                count += 1
            else:
                resources.append(identifier['resource'])
        if count > 1:
            raise serializers.ValidationError("You can only submit one identifier without resource.")

        # Validate if resource values are unique
        if len(resources) != len(set(resources)):
            raise serializers.ValidationError("You can only submit different type of resources.")
        return value

    def validate(self, data):
        eter_id = data.get('eter_id', None)
        deqar_id = data.get('deqar_id', None)
        identifiers = data.get('identifiers', [])
        name_official = data.get('name_official', None)
        locations = data.get('locations', [])
        website_link = data.get('website_link', None)

        #
        # Either ETER or DEQAR or at least one identifier or (name_official, location, website) should
        # be provided.
        #
        if eter_id is not None or deqar_id is not None or len(identifiers) > 0 or \
                (name_official is not None and len(locations) > 0 and website_link is not None):

            institution_eter = None
            institution_deqar = None

            # Check if DEQAR ID exists
            if deqar_id is not None:
                try:
                    institution_deqar = Institution.objects.get(deqar_id=deqar_id)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Please provide valid DEQAR ID.")

            # Check if ETER ID exists
            if eter_id is not None:
                try:
                    institution_eter = InstitutionETERRecord.objects.get(eter_id=eter_id)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Please provide valid ETER ID.")

            # If both ETER ID and DEQAR ID were submitted they should resolve the same institution
            if institution_deqar is not None and institution_eter is not None:
                if institution_deqar.eter_id != institution_eter.id:
                    raise serializers.ValidationError("The provided DEQAR and ETER ID does not match.")
        else:
            raise serializers.ValidationError("This report cannot be linked to an institution. "
                                              "It is missing either a valid ETER ID, DEQAR ID, or local identifier "
                                              "or a combination of institution official name, location and website. ")

        # Name official transliterated can only exists, when name official was submitted
        name_official = data.get('name_official', None)
        name_official_transliterated = data.get('name_official_transliterated', None)

        if name_official is None and name_official_transliterated is not None:
            raise serializers.ValidationError("Please submit name_official if you submitted the transliterated version.")

        return data


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
                                      label='Programme NQF level (Either this or QF EHEA level is required)',
                                      help_text='example: "level 6"')
    qf_ehea_level = QFEHEALevelField(required=False,
                                     label='Prgoramme QF EHEA level (Either this or NQF level is required)',
                                     help_text='accepted values: "0", "1", "2", "3", "short cycle", '
                                               '"first cycle", "second cycle", "third cycle"')

    def validate_identifiers(self, value):
        # Validate if there is only one identifier without resource id
        count = 0
        resources = []
        for identifier in value:
            if 'resource' not in identifier.keys():
                count += 1
            else:
                resources.append(identifier['resource'])
        if count > 1:
            raise serializers.ValidationError("You can only submit one identifier without resource.")

        # Validate if resource values are unique
        if len(resources) != len(set(resources)):
            raise serializers.ValidationError("You can only submit different type of resources.")
        return value


class ReportFileSerializer(serializers.Serializer):
    original_location = serializers.URLField(max_length=500, required=False, label='The URL of the report file',
                                             help_text='example: "http://estudis.aqu.cat/MAD2014_UPC_es.pdf"')
    display_name = serializers.CharField(max_length=255, required=False, label='Display value of the file',
                                         help_text='example: "Ev. de la Solicitud de Verification de Título oficial"')
    report_language = serializers.ListField(child=ReportLanguageField(required=True), required=True,
                                            label='Language(s) of the report',
                                            help_text='example: ["eng", "ger"]')


class ReportLinkSerializer(serializers.Serializer):
    link = serializers.URLField(max_length=255, required=True,
                                label="Links to the Report records/pages on the Agency's website.",
                                help_text='example: "http://srv.aneca.es/ListadoTitulos/node/1182321350"')
    link_display_name = serializers.CharField(max_length=200, required=False,
                                              label='Display the report records link.',
                                              help_text='example: "General information on programme"')


class SubmissionPackageSerializer(serializers.Serializer):
    # Report Identifier
    report_id = ReportIdentifierField(required=False, label='DEQAR identifier of the report')

    # Report Creator
    agency = AgencyField(required=True, label='Identifier or the acronym of the agency',
                         help_text='examples: "33", "ACQUIN"')

    # Record Identification
    local_identifier = serializers.CharField(max_length=255, required=False, label='Local identifier of the report',
                                             help_text='example: "QAA1153-March15"')

    # Report Activity
    activity = serializers.CharField(max_length=500, required=False,
                                     label='Identifier or the description of the Agency ESG Activity',
                                     help_text='examples: "2", "institutional audit"')
    activity_local_identifier = serializers.CharField(max_length=200, required=False,
                                                      label='Local identifier of the ESG Activity',
                                                      help_text='example: "inst_audit')

    # Report Details
    status = ReportStatusField(required=True, label='Identifier or the status of the report',
                               help_text='accepted values: "1", "2", "part of obligatory EQA system", "voluntary"')
    decision = ReportDecisionField(required=True, label='Identifier or the decision described in the report',
                                   help_text='accepted values: "1", "2", "3", "4", "positive", '
                                             '"positive with conditions or restrictions", "no, negative", '
                                             '"not applicable"')

    # Report Validity
    valid_from = serializers.CharField(max_length=20, required=True, label='Starting date of the report validity',
                                       help_text='example: 15-01-2015')
    valid_to = serializers.CharField(max_length=20, required=False, label='End date of the report validity',
                                     help_text='example: 15-01-2015')
    date_format = serializers.CharField(max_length=20, required=True, label='The date format of the validation dates.',
                                        help_text='example: %d-%M-%Y')

    # Report Links
    report_links = ReportLinkSerializer(many=True, required=False)

    # Report Files
    report_files = ReportFileSerializer(many=True, required=True)

    # Institutions
    institutions = InstitutionSerializer(many=True, required=True,
                                         label='Institution(s) which are the subject of the report. '
                                               '(If programme information is submitted, then the report considered '
                                               'to be about the programme itself.)')

    # Programmes
    programmes = ProgrammeSerializer(many=True, required=False,
                                     label='rogramme(s) which are the subject of the report. '
                                           '(If programme information is NOT submitted, then the report considered '
                                           'to be about the institution.)')

    def to_internal_value(self, data):
        errors = []
        data = super(SubmissionPackageSerializer, self).to_internal_value(data)

        agency = data.get('agency', None)
        #
        # Validate if report_id and local_identifier resolving to the same record,
        # or local_identifier is non-existent
        #
        report = data.get('report_id', None)
        local_identifier = data.get('local_identifier', None)

        if report and local_identifier:
            try:
                report_with_local_id = Report.objects.get(agency=agency, local_identifier=local_identifier)
                if report.id != report_with_local_id.id:
                    errors.append("The submitted report_id is pointing to a different report, "
                                  "than the submitted local identifier.")
            except ObjectDoesNotExist:
                pass

        #
        # Validate if date format is applicable, default format is %Y-%m-%d
        #
        date_format = data.get('date_format', '%Y-%m-%d')
        valid_from = data.get('valid_from')
        valid_to = data.get('valid_to', None)
        date_from = None
        date_to = None

        try:
            date_from = datetime.strptime(valid_from, date_format)
            data['valid_from'] = date_from.strftime("%Y-%m-%d")
            if valid_to:
                date_to = datetime.strptime(valid_to, date_format)
                data['valid_to'] = date_to.strftime("%Y-%m-%d")
        except ValueError:
            errors.append("Date format string is not applicable to the submitted date.")

        # Validate if valid_to date is larger than valid_from
        if date_to:
            if date_from >= date_to:
                errors.append("Report's validity start should be earlier then validity end.")

        #
        # Validate if Agency registration start is earlier then report validation start date.
        #
        if date_from:
            if datetime.date(date_from) < agency.registration_start:
                errors.append("Report's validity date must fall after the Agency was registered with EQAR.")

        #
        # Validate if ESG Activity or local identifier is submitted and they can be used to resolve records.
        #
        activity = data.get('activity', None)
        activity_local_identifier = data.get('activity_local_identifier', None)

        if activity is not None or activity_local_identifier is not None:
            if activity is not None:
                if activity.isdigit():
                    try:
                        data['esg_activity'] = AgencyESGActivity.objects.get(pk=activity, agency=agency)
                    except ObjectDoesNotExist:
                        errors.append("Please provide valid ESG Activity ID.")
                else:
                    try:
                        data['esg_activity'] = AgencyESGActivity.objects.get(activity__iexact=activity, agency=agency)
                    except ObjectDoesNotExist:
                        errors.append("Please provide valid ESG Activity.")

            if activity_local_identifier is not None:
                try:
                    data['esg_activity'] = AgencyESGActivity.objects.get(
                        activity_local_identifier=activity_local_identifier, agency=agency)
                except ObjectDoesNotExist:
                    errors.append("Please provide valid ESG Activity local identifier.")
        else:
            errors.append("Either ESG Activity ID, ESG Activity text or ESG Activity local identifier is needed.")

        # Check if Institution ID exists
        institutions = data.get('institutions', [])
        inst_exists = False

        for institution in institutions:
            eter_id = institution.get('eter_id', None)
            deqar_id = institution.get('deqar_id', None)

            name_official = institution.get('name_official', None)
            locations = institution.get('locations', [])
            website_link = institution.get('website_link', None)

            if eter_id is None and deqar_id is None:
                identifiers = institution.get('identifiers', [])
                institutions = set()
                for idf in identifiers:
                    identifier = idf.get('identifier', None)
                    resource = idf.get('resource', 'local identifier')
                    try:
                        if resource == 'local identifier':
                            inst = InstitutionIdentifier.objects.get(
                                identifier=identifier,
                                resource=resource,
                                agency=agency
                            )
                            institutions.add(inst.id)
                        else:
                            inst = InstitutionIdentifier.objects.get(
                                identifier=identifier,
                                resource=resource
                            )
                            institutions.add(inst.id)
                    except ObjectDoesNotExist:
                        pass

                    # Inspect the unique list of identified institutions
                    if len(institutions) > 1:
                        errors.append("The submitted institution identifiers are identifying "
                                                          "more institutions. Please correct them.")
                    if len(institutions) == 1:
                        inst_exists = True

                if not inst_exists:
                    if name_official is None or len(locations) == 0 or website_link is None:
                        errors.append("This report cannot be linked to an institution. "
                                      "It is missing a combination of institution official name, "
                                      "location and website. ")

        #
        # If there are errors raise ValidationError
        #
        if errors:
            raise serializers.ValidationError({settings.NON_FIELD_ERRORS_KEY: errors})
        return data

    def validate(self, data):
        #
        # WP01-008-002
        #
        institutions = data.get('institutions', None)
        programmes = data.get('programmes', None)
        esg_activity = data.get('esg_activity', None)

        # institutional
        if esg_activity.activity_type_id == 2:
            if programmes is not None:
                raise serializers.ValidationError("Please remove programme information "
                                                  "with this particular Activity type.")
        # programme or institutional/programme
        elif esg_activity.activity_type_id == 1 or esg_activity.activity_type_id == 4:
            if len(institutions) > 1:
                raise serializers.ValidationError("Please provide only one institution "
                                                  "with this particular Activity type.")
            if programmes is None:
                raise serializers.ValidationError("Please provide at least one programme "
                                                  "with this particular Activity type.")
        # joint programme
        else:
            if len(institutions) == 1:
                raise serializers.ValidationError("Please provide data for all of the institutions "
                                                  "with this particular Activity type.")
            if programmes is None:
                raise serializers.ValidationError("Please provide at least one programme "
                                                  "with this particular Activity type.")

        return data
