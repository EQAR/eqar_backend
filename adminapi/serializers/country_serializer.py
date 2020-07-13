from drf_writable_nested import UniqueFieldsMixin
from rest_framework import serializers

from countries.models import Country


class CountryListSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member']