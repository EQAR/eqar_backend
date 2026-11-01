from rest_framework import serializers

from webapi.v2.serializers.agency_serializers import AgencyDetailSerializer
from webapi.v2.serializers.institution_serializers import InstitutionDetailSerializer, \
    InstitutionCountryDetailSerializer
from webapi.v2.serializers.report_detail_serializers import ReportDetailSerializer


def _without(fields, *excluded):
    return [ f for f in fields if f not in excluded ]


class McpReportDetailSerializer(ReportDetailSerializer):
    """
    report details, without the link to the authenticated API, the expensive related-institution lists and the
    legacy single-activity fields
    """
    class Meta(ReportDetailSerializer.Meta):
        fields = _without(ReportDetailSerializer.Meta.fields,
                          'agency_url', 'institutions_hierarchical', 'institutions_historical',
                          'agency_esg_activity', 'agency_esg_activity_type')


class McpAgencyDetailSerializer(AgencyDetailSerializer):
    """
    agency details, without personal contact data and change history
    """
    class Meta(AgencyDetailSerializer.Meta):
        fields = _without(AgencyDetailSerializer.Meta.fields,
                          'contact_person', 'phone_numbers', 'emails', 'logo', 'historical_data')


class McpInstitutionCountrySerializer(InstitutionCountryDetailSerializer):
    """
    institution location with the country name only, instead of the country details
    """
    country = serializers.StringRelatedField()


class McpInstitutionDetailSerializer(InstitutionDetailSerializer):
    """
    institution details, without internal search filters and change history
    """
    countries = McpInstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')

    class Meta(InstitutionDetailSerializer.Meta):
        fields = _without(InstitutionDetailSerializer.Meta.fields, 'meili_filters', 'historical_data')
