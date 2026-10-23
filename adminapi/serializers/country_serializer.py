from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework import serializers

from countries.models import Country, CountryQAARegulation
from lists.models import PermissionType, Flag


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member']


class PermissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionType
        fields = '__all__'


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        ref_name = 'CountryFlagSerializer'
        fields = '__all__'


class CountryQAARegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryQAARegulation
        exclude = ('country',)
        read_only_fields = ('group',)


class CountryReadSerializer(serializers.ModelSerializer):
    parent = CountryListSerializer()
    external_QAA_is_permitted = PermissionTypeSerializer()
    european_approach_is_permitted = PermissionTypeSerializer()
    ehea_key_commitment = PermissionTypeSerializer()
    flag = FlagSerializer()
    qaa_regulations = CountryQAARegulationSerializer(many=True, source='countryqaaregulation_set')

    class Meta:
        model = Country
        fields = '__all__'


class CountryWriteSerializer(WritableNestedModelSerializer):
    qaa_regulations = CountryQAARegulationSerializer(many=True, source='countryqaaregulation_set', required=False)

    class Meta:
        model = Country
        fields = '__all__'
