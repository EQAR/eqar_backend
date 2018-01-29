from rest_framework import serializers
from rest_framework.fields import ListField


class AlternativeNameSerializer(serializers.Serializer):
    name_alternative = serializers.CharField(max_length=200, required=False)
    name_alternative_transliterated = serializers.CharField(max_length=200, required=False)


class IdentifierSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255, required=False)
    resource = serializers.CharField(max_length=255, required=False)


class QFEHEALevelSerializer(serializers.Serializer):
    qf_ehea_level_id = serializers.IntegerField(required=False)
    qf_ehea_level = serializers.CharField(max_length=10, required=False)


class InstitutionLocatonSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=3, required=False)
    city = serializers.CharField(max_length=100, required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)


class InstitutionSerializer(serializers.Serializer):
    # Reference
    deqar_id = serializers.CharField(max_length=25, required=False)
    eter_id = serializers.CharField(max_length=15, required=False)

    # Identification
    identifiers = IdentifierSerializer(many=True)

    # Name
    name_official = serializers.CharField(max_length=255, required=False)
    name_official_transliterated = serializers.CharField(max_length=255, required=False)
    name_english = serializers.CharField(max_length=255, required=False)
    acronym = serializers.CharField(max_length=30, required=False)
    alternative_names = AlternativeNameSerializer(many=True)

    # Location
    locations = InstitutionLocatonSerializer(many=True)

    # Level
    nqf_levels = ListField(serializers.CharField(max_length=10, required=False))
    qf_ehea_levels = QFEHEALevelSerializer(many=True)

    # Website
    website = serializers.CharField(max_length=200, required=False)


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
    nqf_levels = ListField(serializers.CharField(max_length=10, required=False))
    qf_ehea_levels = QFEHEALevelSerializer(many=True)


class ReportFileSerializer(serializers.Serializer):
    file_original_location = serializers.CharField(max_length=255, required=False)
    display_name = serializers.CharField(max_length=255, required=False)
    report_language = serializers.CharField(max_length=3, required=True)


class ReportLinkSerializer(serializers.Serializer):
    link = serializers.URLField(max_length=255, required=True)
    link_display_name = serializers.CharField(max_length=200, required=False)


class SubmissionPackageSerializer(serializers.Serializer):
    # Report Creator
    agency_acronym = serializers.CharField(max_length=20, required=False)
    agency_deqar_id = serializers.IntegerField(required=False)

    # Record Identification
    local_identifier = serializers.CharField(max_length=255, required=False)

    # Report Activity
    esg_activity_id = serializers.IntegerField(required=False)
    activity = serializers.CharField(max_length=500, required=False)
    activity_local_identifier = serializers.CharField(max_length=20, required=False)

    # Report Details
    status_id = serializers.IntegerField(required=False)
    status = serializers.CharField(max_length=50, required=False)
    decision_id = serializers.IntegerField(required=False)
    decision = serializers.CharField(max_length=50, required=False)

    # Report Validity
    valid_from = serializers.CharField(max_length=20, required=True)
    valid_to = serializers.CharField(max_length=20, required=False)
    date_format = serializers.CharField(max_length=20, required=True)

    # Report Links
    report_links = ReportLinkSerializer(many=True)

    # Report Files
    report_files = ReportFileSerializer(many=True)

    # Institutions
    institutions = InstitutionSerializer(many=True)

    # Programmes
    programmes = ProgrammeSerializer(many=True)

