from rest_framework import serializers
from agencies.models import *
from lists.models import Country


class CountryListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="discovery_api:country-detail")

    class Meta:
        model = Country
        fields = ['id', 'url', 'country_name_en', 'alpha2', 'alpha3']


class CountryAgencyFocusSerializer(serializers.ModelSerializer):
    agency_id = serializers.HyperlinkedRelatedField(read_only=True, source='agency',
                                                    view_name="discovery_api:agency-detail")
    agency_name = serializers.StringRelatedField(read_only=True, source='agency')

    class Meta:
        model = AgencyFocusCountry
        fields = ['agency_id', 'agency_name']


class CountryAgencyLocatedSerializer(serializers.ModelSerializer):
    agency_id = serializers.HyperlinkedIdentityField(read_only=True, source='agency',
                                                     view_name="discovery_api:agency-detail")
    agency_name = serializers.CharField(read_only=True, source='__str__')

    class Meta:
        model = AgencyFocusCountry
        fields = ['agency_id', 'agency_name']


class CountryDetailSerializer(serializers.ModelSerializer):
    agencies_focused_to = CountryAgencyFocusSerializer(many=True, source='agencyfocuscountry_set')
    agency_located_in = CountryAgencyLocatedSerializer(many=True, read_only=True, source='agency_set')

    class Meta:
        model = Country
        fields = '__all__'
