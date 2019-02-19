from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from institutions.models import Institution, InstitutionCountry, InstitutionIdentifier, InstitutionName, \
    InstitutionNameVersion, InstitutionQFEHEALevel


class InstitutionIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionIdentifier
        fields = ['id', 'agency', 'identifier', 'resource']


class InstitutionNameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionNameVersion
        fields = ['id', 'name', 'transliteration']


class InstitutionNameSerializer(WritableNestedModelSerializer):
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


class InstitutionSerializer(WritableNestedModelSerializer):
    identifiers = InstitutionIdentifierSerializer(many=True, source='institutionidentifier_set')
    names = InstitutionNameSerializer(many=True, source='institutionname_set')
    countries = InstitutionCountrySerializer(many=True, source='institutioncountry_set')
    qf_ehea_levels = InstitutionQFEHEALevelSerializer(many=True, source='institutionqfehealevel_set')

    class Meta:
        model = Institution
        fields = ['id', 'deqar_id', 'name_primary', 'website_link', 'founding_date', 'closure_date',
                  'identifiers', 'names', 'countries', 'qf_ehea_levels']