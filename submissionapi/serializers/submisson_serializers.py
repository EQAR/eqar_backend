from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from agencies.models import AgencyESGActivity
from institutions.models import Institution, InstitutionETERRecord, InstitutionIdentifier
from submissionapi.fields import AgencyField, ReportStatusField, ReportDecisionField, ReportLanguageField, \
    QFEHEALevelField, CountryField


class IdentifierSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255, required=True)
    resource = serializers.CharField(max_length=255, required=False)


class InstitutionAlternativeNameSerializer(serializers.Serializer):
    name_alternative = serializers.CharField(max_length=200, required=True)
    name_alternative_transliterated = serializers.CharField(max_length=200, required=False)


class InstitutionLocatonSerializer(serializers.Serializer):
    country = CountryField(required=True)
    city = serializers.CharField(max_length=100, required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

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
    deqar_id = serializers.CharField(max_length=25, required=False)
    eter_id = serializers.CharField(max_length=15, required=False)

    # Identification
    identifiers = IdentifierSerializer(many=True, required=False)

    # Name
    name_official = serializers.CharField(max_length=255, required=False)
    name_official_transliterated = serializers.CharField(max_length=255, required=False)
    name_english = serializers.CharField(max_length=255, required=False)
    acronym = serializers.CharField(max_length=30, required=False)
    alternative_names = InstitutionAlternativeNameSerializer(many=True, required=False)

    # Location
    locations = InstitutionLocatonSerializer(many=True, required=False)

    # Level
    qf_ehea_levels = serializers.ListField(child=QFEHEALevelField(required=False), required=False)

    # Website
    website_link = serializers.URLField(max_length=200, required=False)

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
    name_alternative = serializers.CharField(max_length=200, required=True)
    qualification_alternative = serializers.CharField(max_length=200, required=False)


class ProgrammeSerializer(serializers.Serializer):
    # Identification
    identifiers = IdentifierSerializer(many=True, required=False)

    # Name
    name_primary = serializers.CharField(max_length=255, required=True)
    qualification_primary = serializers.CharField(max_length=255, required=False)
    alternative_names = ProgrammeAlternativeNameSerializer(many=True, required=False)

    # Country
    countries = serializers.ListField(child=CountryField(required=False), required=False)

    # Level
    nqf_level = serializers.ChoiceField(choices=[('level 6', 'level 6'),
                                                 ('level 7', 'level 7'),
                                                 ('level 8', 'level 8')], required=False)
    qf_ehea_level = QFEHEALevelField(required=False)

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
    original_location = serializers.URLField(max_length=255, required=False)
    display_name = serializers.CharField(max_length=255, required=False)
    report_language = serializers.ListField(child=ReportLanguageField(required=True), required=True)


class ReportLinkSerializer(serializers.Serializer):
    link = serializers.URLField(max_length=255, required=True)
    link_display_name = serializers.CharField(max_length=200, required=False)


class SubmissionPackageSerializer(serializers.Serializer):
    # Report Creator
    agency = AgencyField(required=True)

    # Record Identification
    local_identifier = serializers.CharField(max_length=255, required=False)

    # Report Activity
    activity = serializers.CharField(max_length=500, required=False)
    activity_local_identifier = serializers.CharField(max_length=20, required=False)

    # Report Details
    status = ReportStatusField(required=True)
    decision = ReportDecisionField(required=True)

    # Report Validity
    valid_from = serializers.CharField(max_length=20, required=True)
    valid_to = serializers.CharField(max_length=20, required=False)
    date_format = serializers.CharField(max_length=20, required=True)

    # Report Links
    report_links = ReportLinkSerializer(many=True, required=False)

    # Report Files
    report_files = ReportFileSerializer(many=True, required=True)

    # Institutions
    institutions = InstitutionSerializer(many=True, required=True)

    # Programmes
    programmes = ProgrammeSerializer(many=True, required=False)

    def to_internal_value(self, data):
        errors = []
        data = super(SubmissionPackageSerializer, self).to_internal_value(data)

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
        agency = data.get('agency', None)
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
                        activity_local_identifier=activity_local_identifier)
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
                for idf in identifiers:
                    identifier = idf.get('identifier', None)
                    resource = idf.get('resource', 'local identifier')
                    try:
                        InstitutionIdentifier.objects.get(
                            identifier=identifier,
                            resource=resource,
                            agency=agency
                        )
                        inst_exists = True
                    except ObjectDoesNotExist:
                        pass

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
