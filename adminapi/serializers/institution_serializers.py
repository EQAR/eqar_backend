from drf_writable_nested import WritableNestedModelSerializer, UniqueFieldsMixin
from rest_framework import serializers

from adminapi.serializers.select_serializers import CountrySelectSerializer, AgencySelectSerializer
from countries.models import Country
from eqar_backend.serializers import InstitutionIdentifierTypeSerializer, InstitutionNameTypeSerializer
from institutions.models import Institution, InstitutionCountry, InstitutionIdentifier, InstitutionName, \
    InstitutionNameVersion, InstitutionQFEHEALevel, InstitutionHierarchicalRelationship, InstitutionFlag, \
    InstitutionUpdateLog, InstitutionHistoricalRelationship, InstitutionHistoricalRelationshipType
from lists.models import Flag


class InstitutionIdentifierReadSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    agency = AgencySelectSerializer()

    class Meta:
        model = InstitutionIdentifier
        list_serializer_class = InstitutionIdentifierTypeSerializer
        fields = ['id', 'agency', 'identifier', 'resource', 'note', 'identifier_valid_from', 'identifier_valid_to']


class InstitutionIdentifierWriteSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = InstitutionIdentifier
        list_serializer_class = InstitutionIdentifierTypeSerializer
        fields = ['id', 'agency', 'identifier', 'resource', 'note', 'identifier_valid_from', 'identifier_valid_to']


class InstitutionNameVersionSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = InstitutionNameVersion
        fields = ['id', 'name', 'transliteration']


class InstitutionNameSerializer(UniqueFieldsMixin, WritableNestedModelSerializer):
    alternative_names = InstitutionNameVersionSerializer(many=True, source='institutionnameversion_set', required=False)

    class Meta:
        model = InstitutionName
        list_serializer_class = InstitutionNameTypeSerializer
        fields = ['id', 'name_official', 'name_official_transliterated', 'name_english', 'acronym',
                  'name_valid_to', 'alternative_names', 'name_source_note']


class InstitutionCountryReadSerializer(WritableNestedModelSerializer):
    country = CountrySelectSerializer(required=False)

    class Meta:
        model = InstitutionCountry
        fields = ['id', 'country', 'city', 'lat', 'long', 'country_valid_from', 'country_valid_to']


class InstitutionCountryWriteSerializer(WritableNestedModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = InstitutionCountry
        fields = ['id', 'country', 'city', 'lat', 'long', 'country_valid_from', 'country_valid_to']


class InstitutionQFEHEALevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionQFEHEALevel
        fields = ['id', 'qf_ehea_level']


class InstitutionRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name_primary']


class InstitutionParentReadSerializer(serializers.ModelSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_parent')

    class Meta:
        model = InstitutionHierarchicalRelationship
        fields = ['id', 'institution', 'relationship_note', 'valid_from', 'valid_to']


class InstitutionParentWriteSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(source='institution_parent', queryset=Institution.objects.all())

    class Meta:
        model = InstitutionHierarchicalRelationship
        fields = ['id', 'institution', 'relationship_note', 'valid_from', 'valid_to']


class InstitutionChildReadSerializer(serializers.ModelSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_child')

    class Meta:
        model = InstitutionHierarchicalRelationship
        fields = ['id', 'institution', 'relationship_note', 'valid_from', 'valid_to']


class InstitutionChildWriteSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(source='institution_child', queryset=Institution.objects.all())

    class Meta:
        model = InstitutionHierarchicalRelationship
        fields = ['id', 'institution', 'relationship_note', 'valid_from', 'valid_to']


class InstitutionHistoricalRelationshipTypeSerizlier(serializers.ModelSerializer):
    class Meta:
        model = InstitutionHistoricalRelationshipType
        fields = '__all__'


class InstitutionSourceReadSerializer(serializers.ModelSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_source')
    relationship_type = InstitutionHistoricalRelationshipTypeSerizlier()

    class Meta:
        model = InstitutionHistoricalRelationship
        fields = ['id', 'institution', 'relationship_type', 'relationship_note', 'relationship_date']


class InstitutionSourceWriteSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(source='institution_source', queryset=Institution.objects.all())

    class Meta:
        model = InstitutionHistoricalRelationship
        fields = ['id', 'institution', 'relationship_type', 'relationship_note', 'relationship_date']


class InstitutionTargetReadSerializer(serializers.ModelSerializer):
    institution = InstitutionRelationshipSerializer(source='institution_target', read_only=True)
    relationship_type = InstitutionHistoricalRelationshipTypeSerizlier(read_only=True)

    class Meta:
        model = InstitutionHistoricalRelationship
        fields = ['id', 'institution', 'relationship_type', 'relationship_note', 'relationship_date']


class InstitutionTargetWriteSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(source='institution_target', queryset=Institution.objects.all())

    class Meta:
        model = InstitutionHistoricalRelationship
        fields = ['id', 'institution', 'relationship_type', 'relationship_note', 'relationship_date']


class InstitutionFlagReadSerializer(serializers.ModelSerializer):
    flag = serializers.StringRelatedField()

    class Meta:
        model = InstitutionFlag
        fields = ('id', 'flag', 'flag_message', 'active', 'removed_by_eqar')


class InstitutionFlagWriteSerializer(serializers.ModelSerializer):
    flag = serializers.SlugRelatedField(slug_field='flag', queryset=Flag.objects.all())

    class Meta:
        model = InstitutionFlag
        fields = ('id', 'flag', 'flag_message', 'active', 'removed_by_eqar')


class InstitutionUpdateLogSerializer(serializers.ModelSerializer):
    updated_by = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = InstitutionUpdateLog
        fields = ('id', 'note', 'updated_at', 'updated_by')


class InstitutionReadSerializer(serializers.ModelSerializer):
    eter_id = serializers.SlugRelatedField(read_only=True, slug_field='eter_id', source='eter')
    identifiers_national = InstitutionIdentifierReadSerializer(many=True,
                                                           source='institutionidentifier_set',
                                                           context={'type': 'national'})
    identifiers_local = InstitutionIdentifierReadSerializer(many=True,
                                                        source='institutionidentifier_set',
                                                        context={'type': 'local'})
    names_actual = InstitutionNameSerializer(many=True,
                                             source='institutionname_set',
                                             context={'type': 'actual'})
    names_former = InstitutionNameSerializer(many=True,
                                             source='institutionname_set',
                                             context={'type': 'former'})
    countries = InstitutionCountryReadSerializer(many=True, source='institutioncountry_set')
    qf_ehea_levels = InstitutionQFEHEALevelSerializer(many=True, source='institutionqfehealevel_set')
    hierarchical_parent = InstitutionParentReadSerializer(many=True, source='relationship_child')
    hierarchical_child = InstitutionChildReadSerializer(many=True, source='relationship_parent')
    historical_source = InstitutionSourceReadSerializer(many=True, source='relationship_target')
    historical_target = InstitutionTargetReadSerializer(many=True, source='relationship_source')
    flags = InstitutionFlagReadSerializer(many=True, source='institutionflag_set')
    update_log = InstitutionUpdateLogSerializer(many=True, source='institutionupdatelog_set')

    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'eter_id', 'name_primary', 'website_link', 'founding_date', 'closure_date',
                  'identifiers_national', 'identifiers_local', 'names_actual', 'names_former', 'countries',
                  'internal_note', 'other_comment', 'qf_ehea_levels', 'hierarchical_parent', 'hierarchical_child',
                  'historical_source', 'historical_target', 'created_at', 'flags', 'update_log']


class InstitutionWriteSerializer(WritableNestedModelSerializer):
    eter_id = serializers.SlugRelatedField(read_only=True, slug_field='eter_id', source='eter')
    identifiers = InstitutionIdentifierWriteSerializer(many=True, source='institutionidentifier_set', required=False)
    names = InstitutionNameSerializer(many=True, source='institutionname_set')
    countries = InstitutionCountryWriteSerializer(many=True, source='institutioncountry_set')
    qf_ehea_levels = InstitutionQFEHEALevelSerializer(many=True, source='institutionqfehealevel_set', required=False)
    hierarchical_parent = InstitutionParentWriteSerializer(many=True, source='relationship_child', required=False)
    hierarchical_child = InstitutionChildWriteSerializer(many=True, source='relationship_parent', required=False)
    historical_source = InstitutionSourceWriteSerializer(many=True, source='relationship_target', required=False)
    historical_target = InstitutionTargetWriteSerializer(many=True, source='relationship_source', required=False)
    flags = InstitutionFlagWriteSerializer(many=True, source='institutionflag_set')

    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'eter_id', 'name_primary', 'website_link', 'founding_date', 'closure_date',
                  'identifiers', 'names', 'countries',
                  'internal_note', 'other_comment', 'qf_ehea_levels', 'hierarchical_parent', 'hierarchical_child',
                  'historical_source', 'historical_target', 'flags']