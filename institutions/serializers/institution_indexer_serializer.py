from django.db.models import Q

from rest_framework import serializers

from eqar_backend.serializer_fields.date_unix_timestamp import UnixTimestampDateField

from agencies.models import Agency
from countries.models import Country
from programmes.models import Programme, ProgrammeName
from reports.models import Report, ReportFile, ReportLink
from agencies.models import AgencyESGActivity
from institutions.models import \
    Institution, \
    InstitutionIdentifier, \
    InstitutionOrganizationType, \
    InstitutionName, \
    InstitutionNameVersion, \
    InstitutionCountry, \
    InstitutionHierarchicalRelationship


class AgencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Agency
        fields = [
            'id',
            'acronym_primary',
        ]

class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = [  'id',
                    'iso_3166_alpha2',
                    'iso_3166_alpha3',
                    'name_english',
                    'ehea_is_member',
                ]

class InstitutionIdentifierSerializer(serializers.ModelSerializer):

    agency = AgencySerializer()
    resource = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InstitutionIdentifier
        fields = [
            'identifier',
            'agency',
            'resource',
        ]

class InstitutionNameVersionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InstitutionNameVersion
        fields = [
            'name',
            'transliteration'
        ]

class InstitutionNameSerializer(serializers.ModelSerializer):

    name_versions = InstitutionNameVersionSerializer(many=True, read_only=True, source='institutionnameversion_set')
    name_valid_to = UnixTimestampDateField()

    class Meta:
        model = InstitutionName
        fields = [
            'name_official',
            'name_official_transliterated',
            'name_english',
            'name_versions',
            'acronym',
            'name_valid_to'
        ]

class InstitutionOrganizationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = InstitutionOrganizationType
        fields = [
            'id',
            'type'
        ]

class InstitutionCountrySerializer(serializers.ModelSerializer):

    country = CountrySerializer()
    country_valid_from = UnixTimestampDateField()
    country_valid_to = UnixTimestampDateField()

    class Meta:
        model = InstitutionCountry
        fields = [  'country',
                    'city',
                    'lat', 'long',
                    'country_verified',
                    'country_valid_from',
                    'country_valid_to',
                ]

class RelatedInstitutionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Institution
        fields = [
            'id',
            'deqar_id',
            'eter_id',
            'name_primary',
            'name_sort',
            'website_link',
        ]


class ParentInstitutionSerializer(serializers.ModelSerializer):

    institution = RelatedInstitutionSerializer(source='institution_parent')
    relationship_type = serializers.StringRelatedField()
    valid_from = UnixTimestampDateField()
    valid_to = UnixTimestampDateField()

    class Meta:
        model = InstitutionHierarchicalRelationship
        fields = [
            'institution',
            'relationship_type',
            'valid_from',
            'valid_to',
        ]


class ChildInstitutionSerializer(ParentInstitutionSerializer):

    institution = RelatedInstitutionSerializer(source='institution_child')


class InstitutionIndexerSerializer(serializers.ModelSerializer):

    identifiers = InstitutionIdentifierSerializer(many=True, read_only=True, source='institutionidentifier_set')
    organization_type = InstitutionOrganizationTypeSerializer()
    names = InstitutionNameSerializer(many=True, read_only=True, source='institutionname_set')
    founding_date = UnixTimestampDateField()
    closure_date = UnixTimestampDateField()
    locations = InstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')
    part_of = ParentInstitutionSerializer(many=True, read_only=True, source='relationship_child')
    includes = ChildInstitutionSerializer(many=True, read_only=True, source='relationship_parent')
    qf_ehea_levels = serializers.SerializerMethodField()
    created_at = UnixTimestampDateField()
    agencies = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    activity_types = serializers.SerializerMethodField()
    activity_groups = serializers.SerializerMethodField()
    crossborder = serializers.SerializerMethodField()

    def get_qf_ehea_levels(self, obj):
        return [ iqf.qf_ehea_level.level for iqf in obj.institutionqfehealevel_set.all() ]

    def get_crossborder(self, obj):
        crossborder = False
        for report in obj.reports.iterator():
            for ic in obj.institutioncountry_set.filter(country_verified=True):
                if not report.agency.agencyfocuscountry_set.filter(Q(country__id=ic.country.id) & Q(country_is_crossborder=False)):
                    crossborder = True
                    break
            if crossborder:
                break
        return crossborder

    def get_agencies(self, obj):
        return AgencySerializer(Agency.objects.filter(report__institutions=obj).distinct(), many=True).data

    def get_status(self, obj):
        return list(obj.reports.values_list('status__status', flat=True).distinct())

    def get_activity_types(self, obj):
        return list(obj.reports.values_list('agency_esg_activities__activity_group__activity_type__type', flat=True).distinct())

    def get_activity_groups(self, obj):
        return list(obj.reports.values_list('agency_esg_activities__activity_group__id', flat=True).distinct())

    class Meta:
        model = Institution
        fields = [  'id',
                    'deqar_id',
                    'eter_id',
                    'identifiers',
                    'is_other_provider',
                    'organization_type',
                    'name_sort',
                    'name_primary',
                    'names',
                    'website_link',
                    'founding_date',
                    'closure_date',
                    'locations',
                    'part_of',
                    'includes',
                    'qf_ehea_levels',
                    'has_report',
                    'agencies',
                    'status',
                    'activity_types',
                    'activity_groups',
                    'crossborder',
                    'created_at'
                ]
