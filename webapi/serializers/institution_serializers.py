from rest_framework import serializers

from eqar_backend.serializers import HistoryFilteredListSerializer
from institutions.models import Institution, InstitutionIdentifier, InstitutionName, \
    InstitutionHistoricalData, InstitutionCountry, InstitutionQFEHEALevel, InstitutionNameVersion
from webapi.serializers.country_serializers import CountryQARequirementSerializer, CountryDetailSerializer


class InstitutionCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()

    class Meta:
        ref_name = 'InstitutionCountry v1'
        model = InstitutionCountry
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['country', 'city', 'lat', 'long', 'country_verified']


class InstitutionListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:institution-detail")
    countries = InstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')
    hierarchical_relationships = serializers.SerializerMethodField()

    def get_hierarchical_relationships(self, obj):
        includes = []
        part_of = []

        for relation in obj.relationship_parent.all():
            data = InstitutionHierarchicalRelationshipSerializer(relation.institution_child, context=self.context).data
            data['relationship_type'] = relation.relationship_type.type if relation.relationship_type else None
            data['relationship_date_from'] = relation.valid_from if relation.relationship_type else None
            data['relationship_date_to'] = relation.valid_to if relation.relationship_type else None

            includes.append(data)

        for relation in obj.relationship_child.all():
            data = InstitutionHierarchicalRelationshipSerializer(relation.institution_parent, context=self.context).data
            data['relationship_type'] = relation.relationship_type.type if relation.relationship_type else None
            data['relationship_date_from'] = relation.valid_from if relation.relationship_type else None
            data['relationship_date_to'] = relation.valid_to if relation.relationship_type else None
            part_of.append(data)

        return {'includes': includes, 'part_of': part_of}

    class Meta:
        model = Institution
        fields = ['id', 'eter_id', 'url', 'name_primary', 'name_sort', 'website_link', 'countries', 'hierarchical_relationships']


class InstitutionHierarchicalRelationshipSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:institution-detail")

    class Meta:
        ref_name = 'InstitutionHierarchicalRelationship v1'
        model = Institution
        fields = ['id', 'url', 'name_primary', 'website_link']


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField(read_only=True)
    resource = serializers.StringRelatedField(read_only=True)

    class Meta:
        ref_name = 'InstitutionIdentifier v1'
        model = InstitutionIdentifier
        fields = ['identifier', 'agency', 'resource', 'identifier_valid_from', 'identifier_valid_to']


class InstitutionNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = 'InstitutionNameVersion v1'
        model = InstitutionNameVersion
        fields = ['name', 'transliteration']


class InstitutionNameSerializer(serializers.ModelSerializer):
    name_versions = InstitutionNameVersionSerializer(many=True, read_only=True, source='institutionnameversion_set')

    class Meta:
        ref_name = 'InstitutionName v1'
        model = InstitutionName
        fields = ['name_official', 'name_official_transliterated', 'name_english', 'name_versions', 'acronym',
                  'name_source_note', 'name_valid_to']


class InstitutionHistoricalDataSerializer(serializers.ModelSerializer):
    field = serializers.StringRelatedField()

    class Meta:
        ref_name = 'InstitutionHistoricalData v1'
        model = InstitutionHistoricalData
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['field', 'value', 'record_id', 'valid_from', 'valid_to']


class InstitutionQFEHEALevelSerializer(serializers.ModelSerializer):
    qf_ehea_level = serializers.StringRelatedField()

    class Meta:
        ref_name = 'InstitutionQFEHEALevel v1'
        model = InstitutionQFEHEALevel
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['qf_ehea_level', 'qf_ehea_level_source', 'qf_ehea_level_source_note',
                  'qf_ehea_level_valid_from', 'qf_ehea_level_valid_to']


class InstitutionCountryDetailSerializer(serializers.ModelSerializer):
    country = CountryDetailSerializer()

    class Meta:
        ref_name = 'InstitutionCountry v1'
        model = InstitutionCountry
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['country', 'city', 'lat', 'long', 'country_source', 'country_source',
                  'country_valid_from', 'country_valid_to', 'country_verified']


class InstitutionDetailSerializer(serializers.ModelSerializer):
    eter =serializers.StringRelatedField()
    identifiers = InstitutionIdentifierSerializer(many=True, read_only=True, source='institutionidentifier_set')
    names = InstitutionNameSerializer(many=True, read_only=True, source='institutionname_set')
    countries = InstitutionCountryDetailSerializer(many=True, read_only=True, source='institutioncountry_set')
    # nqf_levels = serializers.StringRelatedField(many=True, read_only=True, source='institutionnqflevel_set')
    qf_ehea_levels = InstitutionQFEHEALevelSerializer(many=True, read_only=True, source='institutionqfehealevel_set')
    historical_relationships = serializers.SerializerMethodField()
    hierarchical_relationships = serializers.SerializerMethodField()
    historical_data = InstitutionHistoricalDataSerializer(many=True, read_only=True, source='institutionhistoricaldata_set')

    def get_hierarchical_relationships(self, obj):
        includes = []
        part_of = []

        for relation in obj.relationship_parent.all():
            includes.append(InstitutionListSerializer(relation.institution_child, context=self.context).data)

        for relation in obj.relationship_child.all():
            part_of.append(InstitutionListSerializer(relation.institution_parent, context=self.context).data)

        return {'includes': includes, 'part_of': part_of}

    def get_historical_relationships(self, obj):
        relationships = []

        for relation in obj.relationship_source.all():
            relationships.append({
                'institution': InstitutionListSerializer(relation.institution_target, context=self.context).data,
                'relationship_type': relation.relationship_type.type_to,
                'relationship_date': relation.relationship_date
            })

        for relation in obj.relationship_target.all():
            relationships.append({
                'institution': InstitutionListSerializer(relation.institution_source, context=self.context).data,
                'relationship_type': relation.relationship_type.type_from,
                'relationship_date': relation.relationship_date
            })
        return relationships

    class Meta:
        ref_name = 'Institution v1'
        model = Institution
        fields = ('id', 'eter', 'identifiers', 'website_link', 'names', 'countries', 'founding_date', 'closure_date',
                  'is_other_provider', 'historical_relationships', 'hierarchical_relationships', 'qf_ehea_levels', 'historical_data')


class InstitutionDEQARConnectListSerializer(serializers.HyperlinkedModelSerializer):
    city = serializers.SlugRelatedField(read_only=True, slug_field='city', many=True, source='institutioncountry_set')
    country = serializers.SlugRelatedField(read_only=True, slug_field='country__name_english', many=True, source='institutioncountry_set')
    has_more = serializers.BooleanField(read_only=True)

    class Meta:
        ref_name = 'Institution'
        model = Institution
        fields = ['id', 'deqar_id', 'eter_id', 'name_primary', 'website_link', 'city', 'country', 'has_more']
