from rest_framework import serializers
from agencies.models import *
from lists.models import Country


class CountryListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:country-detail")

    class Meta:
        model = Country
        fields = ['id', 'url', 'country_name_en', 'alpha2', 'alpha3']


class CountryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'country_name_en', 'alpha2', 'alpha3', 'qa_requirement_notes']
