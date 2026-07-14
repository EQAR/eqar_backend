from rest_framework import serializers

from eqar_backend.serializers import HistoryFilteredListSerializer
from institutions.models import Institution, InstitutionIdentifier, InstitutionName, \
    InstitutionHistoricalData, InstitutionCountry, InstitutionQFEHEALevel, InstitutionNameVersion, \
    InstitutionOrganizationType, InstitutionHierarchicalRelationship, InstitutionHistoricalRelationship
from lists.models import IdentifierResource
from webapi.v2.serializers.country_serializers import CountryDetailSerializer
from webapi.v2.views.report_views import institution_report_meili_filters

class InstitutionCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()

    class Meta:
        model = InstitutionCountry
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['country', 'city', 'lat', 'long', 'country_verified']


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField(read_only=True)
    resource = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InstitutionIdentifier
        fields = ['identifier', 'agency', 'resource', 'identifier_valid_from', 'identifier_valid_to']


class InstitutionNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionNameVersion
        fields = ['name', 'transliteration']


class InstitutionNameSerializer(serializers.ModelSerializer):
    name_versions = InstitutionNameVersionSerializer(many=True, read_only=True, source='institutionnameversion_set')

    class Meta:
        model = InstitutionName
        fields = ['name_official', 'name_official_transliterated', 'name_english', 'name_versions', 'acronym',
                  'name_source_note', 'name_valid_to']


class InstitutionHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField()

    class Meta:
        model = InstitutionHistoricalData
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['field', 'value', 'record_id', 'valid_from', 'valid_to']


class InstitutionQFEHEALevelSerializer(serializers.ModelSerializer):
    qf_ehea_level = serializers.StringRelatedField()

    class Meta:
        model = InstitutionQFEHEALevel
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['qf_ehea_level', 'qf_ehea_level_source', 'qf_ehea_level_source_note',
                  'qf_ehea_level_valid_from', 'qf_ehea_level_valid_to']


class InstitutionCountryDetailSerializer(serializers.ModelSerializer):
    country = CountryDetailSerializer()

    class Meta:
        model = InstitutionCountry
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['country', 'city', 'lat', 'long', 'country_source', 'country_source',
                  'country_valid_from', 'country_valid_to', 'country_verified']


class InstitutionRelationshipSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v2:institution-detail")
    countries = InstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')

    class Meta:
        model = Institution
        fields = ['id', 'eter_id', 'url', 'name_primary', 'name_sort', 'website_link', 'countries']


class ParentInstitutionSerializer(serializers.ModelSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_parent')
    relationship_type = serializers.StringRelatedField()

    class Meta:
        model = InstitutionHierarchicalRelationship
        fields = [
            'institution',
            'relationship_type',
            'valid_from',
            'valid_to',
        ]

class ChildInstitutionSerializer(ParentInstitutionSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_child')


class HistoricalTargetSerializer(serializers.ModelSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_target')
    relationship_type = serializers.CharField(source='relationship_type.type_to')

    class Meta:
        model = InstitutionHistoricalRelationship
        fields = [
            'institution',
            'relationship_type',
            'relationship_date'
        ]

class HistoricalSourceSerializer(HistoricalTargetSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_source')
    relationship_type = serializers.CharField(source='relationship_type.type_from')


class InstitutionOrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionOrganizationType
        fields = ['id', 'type']


class InstitutionDetailSerializer(serializers.ModelSerializer):
    identifiers = InstitutionIdentifierSerializer(many=True, read_only=True, source='institutionidentifier_set')
    names = InstitutionNameSerializer(many=True, read_only=True, source='institutionname_set')
    countries = InstitutionCountryDetailSerializer(many=True, read_only=True, source='institutioncountry_set')
    qf_ehea_levels = InstitutionQFEHEALevelSerializer(many=True, read_only=True, source='institutionqfehealevel_set')
    historical_relationships = serializers.SerializerMethodField()
    hierarchical_relationships = serializers.SerializerMethodField()
    historical_data = InstitutionHistoricalDataSerializer(many=True, read_only=True, source='institutionhistoricaldata_set')
    organization_type = InstitutionOrganizationTypeSerializer()
    meili_filters = serializers.SerializerMethodField()
    is_orgreg_alliance = serializers.SerializerMethodField()

    def get_is_orgreg_alliance(self, obj):
        return obj.is_orgreg_alliance()

    def get_hierarchical_relationships(self, obj):
        return {
            'includes': ChildInstitutionSerializer(obj.relationship_parent.all(), many=True, context=self.context).data,
            'part_of': ParentInstitutionSerializer(obj.relationship_child.all(), many=True, context=self.context).data
        }

    def get_historical_relationships(self, obj):
        return HistoricalTargetSerializer(obj.relationship_source.all(), many=True, context=self.context).data + \
               HistoricalSourceSerializer(obj.relationship_target.all(), many=True, context=self.context).data

    def get_meili_filters(self, obj):
        return {
            'reports': institution_report_meili_filters(obj, 'INDEX_REPORTS'),
            'programmes': institution_report_meili_filters(obj, 'INDEX_PROGRAMMES'),
        }

    class Meta:
        model = Institution
        fields = ('id', 'eter_id', 'identifiers', 'website_link', 'names', 'countries', 'founding_date', 'closure_date',
                  'historical_relationships', 'hierarchical_relationships', 'meili_filters', 'qf_ehea_levels',
                  'is_other_provider', 'organization_type', 'is_orgreg_alliance', 'source_of_information', 'historical_data')


class InstitutionResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentifierResource
        fields = ['resource', 'title', 'source', 'link']


class InstitutionDEQARConnectListSerializer(serializers.HyperlinkedModelSerializer):
    city = serializers.SlugRelatedField(read_only=True, slug_field='city', many=True, source='institutioncountry_set')
    country = serializers.SlugRelatedField(read_only=True, slug_field='country__name_english', many=True, source='institutioncountry_set')
    has_more = serializers.BooleanField(read_only=True)

    class Meta:
        ref_name = 'Institution'
        model = Institution
        fields = ['id', 'deqar_id', 'eter_id', 'name_primary', 'website_link', 'city', 'country', 'has_more']
