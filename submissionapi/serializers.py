from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.fields import ListField

from agencies.models import AgencyESGActivity, Agency
from countries.models import Country
from institutions.models import Institution, InstitutionETERRecord
from lists.models import QFEHEALevel, Language
from reports.models import ReportStatus, ReportDecision


class AlternativeNameSerializer(serializers.Serializer):
    name_alternative = serializers.CharField(max_length=200, required=False)
    name_alternative_transliterated = serializers.CharField(max_length=200, required=False)


class IdentifierSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255, required=False)
    resource = serializers.CharField(max_length=255, required=False)


class QFEHEALevelSerializer(serializers.Serializer):
    qf_ehea_level = serializers.CharField(max_length=20, required=False)

    def validate_qf_ehea_level(self, value):
        if value.isdigit():
            try:
                QFEHEALevel.objects.get(code=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid QF EHEA ID.")
        else:
            try:
                QFEHEALevel.objects.get(level=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid QF EHEA level.")
        return value


class InstitutionLocatonSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=3, required=False)
    city = serializers.CharField(max_length=100, required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    def validate_country(self, value):
        value = value.upper()
        if len(value) == 2:
            try:
                Country.objects.get(iso_3166_alpha2=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid country code.")
        elif len(value) == 3:
            try:
                Country.objects.get(iso_3166_alpha3=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid country code.")
        else:
            raise serializers.ValidationError("Please provide valid country code.")

        return value


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
    alternative_names = AlternativeNameSerializer(many=True, required=False)

    # Location
    locations = InstitutionLocatonSerializer(many=True, required=False)

    # Level
    qf_ehea_levels = QFEHEALevelSerializer(many=True, required=False)

    # Website
    website = serializers.CharField(max_length=200, required=False)

    def validate(self, data):
        eter_id = data.get('eter_id', None)
        deqar_id = data.get('deqar_id', None)
        identifiers = data.get('identifiers', "")
        name_official = data.get('name_official', None)
        locations = data.get('locations', "")
        website_link = data.get('website', None)

        #
        # Either ETER or DEQAR or at least one identifier or (name_official, location, website_link) should
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
            raise serializers.ValidationError("You have to provide either ETER/DEQAR/Identifier to identify institution"
                                              "or name_official and location and website to identify or create a "
                                              "new record.")

        return data


class ProgrammeSerializer(serializers.Serializer):
    # Identification
    identifiers = IdentifierSerializer

    # Name
    name_primary = serializers.CharField(max_length=255, required=False)
    qualification_primary = serializers.CharField(max_length=255, required=False)
    alternative_names = AlternativeNameSerializer(many=True)

    # Country
    countries = ListField(serializers.CharField(max_length=3, required=False))

    # Level
    qf_ehea_levels = QFEHEALevelSerializer(many=True)


class ReportFileSerializer(serializers.Serializer):
    file_original_location = serializers.CharField(max_length=255, required=False)
    display_name = serializers.CharField(max_length=255, required=False)
    report_language = serializers.CharField(max_length=3, required=True)

    def validate_report_language(self, value):
        if len(value) == 2:
            try:
                Language.objects.get(iso_639_1=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid language code.")
        elif len(value) == 3:
            try:
                Language.objects.get(iso_639_2=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid language code.")
        else:
            raise serializers.ValidationError("Please provide valid language code.")


class ReportLinkSerializer(serializers.Serializer):
    link = serializers.URLField(max_length=255, required=True)
    link_display_name = serializers.CharField(max_length=200, required=False)


class SubmissionPackageSerializer(serializers.Serializer):
    # Report Creator
    agency = serializers.CharField(max_length=20, required=True)

    # Record Identification
    local_identifier = serializers.CharField(max_length=255, required=False)

    # Report Activity
    activity = serializers.CharField(max_length=500, required=False)
    activity_local_identifier = serializers.CharField(max_length=20, required=False)

    # Report Details
    status = serializers.CharField(max_length=50, required=True)
    decision = serializers.CharField(max_length=50, required=True)

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

    def validate_agency(self, value):
        """
        Validate if the submitted Agency is valid.
        """
        if value.isdigit():
            try:
                Agency.objects.get(deqar_id=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency DEQAR ID.")
        else:
            try:
                Agency.objects.get(acronym_primary=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency Acronym.")
        return value

    def validate_status(self, value):
        """
        Validate if the submitted ReportStatus is valid.
        """
        if value.isdigit():
            try:
                ReportStatus.objects.get(pk=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Status ID.")
        else:
            try:
                ReportStatus.objects.get(status=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Status.")
        return value

    def validate_decision(self, value):
        """
        Validate if the submitted ReportDecision is valid.
        """
        if value.isdigit():
            try:
                ReportDecision.objects.get(pk=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Decision ID.")
        else:
            try:
                ReportDecision.objects.get(decision=value)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Decision.")
        return value

    def validate(self, data):
        #
        # Validate if date format is applicable, default format is %Y-%m-%d
        #
        date_format = data.get('date_format', '%Y-%m-%d')
        valid_from = data.get('valid_from')
        valid_to = data.get('valid_to', None)

        try:
            datetime.strptime(valid_from, date_format)
            if valid_to:
                datetime.strptime(valid_to, date_format)
        except ValueError:
            raise serializers.ValidationError("Date format string is not applicable to the submitted date.")

        #
        # Validate if ESG Activity or local identifier is submitted and they can be used to resolve records.
        #
        agency = data.get('agency', None)
        activity = data.get('activity', None)
        activity_local_identifier = data.get('activity_local_identifier', None)

        if activity is not None or activity_local_identifier is not None:
            if agency.isdigit():
                agency = Agency.objects.get(deqar_id=agency)
            else:
                agency = Agency.objects.get(acronym_primary=agency)

            if activity is not None:
                if activity.isdigit():
                    try:
                        AgencyESGActivity.objects.get(pk=activity, agency=agency)
                    except ObjectDoesNotExist:
                        raise serializers.ValidationError("Please provide valid ESG Activity ID.")
                else:
                    try:
                        AgencyESGActivity.objects.get(activity=activity, agency=agency)
                    except ObjectDoesNotExist:
                        raise serializers.ValidationError("Please provide valid ESG Activity.")

            if activity_local_identifier is not None:
                try:
                    AgencyESGActivity.objects.get(activity_local_identifier=activity_local_identifier)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Please provide valid ESG Activity local identifier.")
        else:
            raise serializers.ValidationError("Either ESG Activity ID, ESG Activity text or ESG Activity local "
                                              "identifier is needed.")
        return data