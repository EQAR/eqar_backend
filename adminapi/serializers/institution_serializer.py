from rest_framework import serializers
from institutions.models import Institution, InstitutionCountry


class InstitutionCountrySerializer(serializers.ModelSerializer):
    country = serializers.StringRelatedField()

    class Meta:
        model = InstitutionCountry
        fields = ['country', 'city', 'lat', 'long']


class InstitutionSelectListSerializer(serializers.ModelSerializer):
    eter_id = serializers.SlugRelatedField(read_only=True, slug_field='eter_id', source='eter')
    countries = InstitutionCountrySerializer(many=True, read_only=True, source='institutioncountry_set')

    class Meta:
        model = Institution
        fields = ['id', 'eter_id', 'deqar_id', 'name_primary', 'website_link', 'countries']