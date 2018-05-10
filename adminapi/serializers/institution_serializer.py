from rest_framework import serializers
from institutions.models import Institution, InstitutionCountry, InstitutionIdentifier, InstitutionName, \
    InstitutionNameVersion, InstitutionQFEHEALevel


class InstitutionCountrySelectListSerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()

    class Meta:
        model = InstitutionCountry
        fields = ['country', 'city', 'lat', 'long']


class InstitutionSelectListSerializer(serializers.ModelSerializer):
    eter_id = serializers.SlugRelatedField(read_only=True, slug_field='eter_id', source='eter')
    countries = InstitutionCountrySelectListSerializer(many=True, read_only=True, source='institutioncountry_set')

    class Meta:
        model = Institution
        fields = ['id', 'eter_id', 'deqar_id', 'name_primary', 'website_link', 'countries']


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionIdentifier
        fields = ['id', 'agency', 'identifier', 'resource']


class InstitutionNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionNameVersion
        fields = ['id', 'name', 'transliteration']


class InstitutionNameSerializer(serializers.ModelSerializer):
    alternative_names = InstitutionNameVersionSerializer(many=True, source='institutionnameversion_set')

    class Meta:
        model = InstitutionName
        fields = ['id', 'name_official', 'name_official_transliterated', 'name_english', 'acronym',
                  'name_valid_to', 'alternative_names']


class InstitutionCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionCountry
        fields = ['id', 'country', 'city', 'lat', 'long', 'country_valid_from', 'country_valid_to']


class InstitutionQFEHEALevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionQFEHEALevel
        fields = ['id', 'qf_ehea_level']


class InstitutionSerializer(serializers.ModelSerializer):
    identifiers = InstitutionIdentifierSerializer(many=True, source='institutionidentifier_set')
    names = InstitutionNameSerializer(many=True, source='institutionname_set')
    countries = InstitutionCountrySerializer(many=True, source='institutioncountry_set')
    qf_ehea_levels = InstitutionQFEHEALevelSerializer(many=True, source='institutionqfehealevel_set')

    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'website_link', 'founding_date', 'closure_date',
                  'identifiers', 'names', 'countries', 'qf_ehea_levels']