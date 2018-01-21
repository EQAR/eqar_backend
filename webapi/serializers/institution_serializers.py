from rest_framework import serializers

from eqar_backend.serializers import HistoryFilteredListSerializer
from institutions.models import Institution, InstitutionIdentifier, InstitutionName, \
    InstitutionHistoricalData, InstitutionCountry, InstitutionQFEHEALevel


class InstitutionCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()

    class Meta:
        model = InstitutionCountry
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['country', 'city', 'lat', 'long']


class InstitutionListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:institution-detail")
    eter_id = serializers.SlugRelatedField(read_only=True, slug_field='eter_id', source='eter')
    countries = InstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')

    class Meta:
        model = Institution
        fields = ['id', 'eter_id', 'url', 'name_primary', 'website_link', 'countries']


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField(read_only=True)
    resource = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InstitutionIdentifier
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['identifier', 'agency', 'resource', 'identifier_valid_from', 'identifier_valid_to']


class InstitutionNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'translitertion']


class InstitutionNameSerializer(serializers.ModelSerializer):
    name_versions = InstitutionNameVersionSerializer(many=True, read_only=True, source='institutionnameversion_set')

    class Meta:
        model = InstitutionName
        list_serializer_class = HistoryFilteredListSerializer
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


class InstitutionCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()

    class Meta:
        model = InstitutionCountry
        list_serializer_class = HistoryFilteredListSerializer
        fields = ['country', 'city', 'lat', 'long', 'country_source', 'country_source',
                  'country_valid_from', 'country_valid_to']


class InstitutionDetailSerializer(serializers.ModelSerializer):
    eter =serializers.StringRelatedField()
    identifiers = InstitutionIdentifierSerializer(many=True, read_only=True, source='institutionidentifier_set')
    names = InstitutionNameSerializer(many=True, read_only=True, source='institutionname_set')
    countries = InstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')
    # nqf_levels = serializers.StringRelatedField(many=True, read_only=True, source='institutionnqflevel_set')
    qf_ehea_levels = InstitutionQFEHEALevelSerializer(many=True, read_only=True, source='institutionqfehealevel_set')
    historical_data = InstitutionHistoricalDataSerializer(many=True, read_only=True, source='institutionhistoricaldata_set')

    class Meta:
        model = Institution
        fields = ('id', 'eter', 'identifiers', 'website_link', 'names', 'countries', 'qf_ehea_levels', 'historical_data')
