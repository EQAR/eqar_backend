from drf_writable_nested import UniqueFieldsMixin, WritableNestedModelSerializer
from rest_framework import serializers

from adminapi.serializers.select_serializers import CountryQARequirementTypeSerializer
from countries.models import Country, CountryQARequirement, CountryQAARegulation
from lists.models import PermissionType, Flag


class CountryListSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
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
        fields = '__all__'


class CountryQARequirementReadSerializer(serializers.ModelSerializer):
    qa_requirement_type = CountryQARequirementTypeSerializer()

    class Meta:
        model = CountryQARequirement
        fields = '__all__'


class CountryQARequirementWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryQARequirement
        fields = '__all__'


class CountryQAARegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryQAARegulation
        fields = '__all__'


class CountryReadSerializer(serializers.ModelSerializer):
    external_QAA_is_permitted = PermissionTypeSerializer()
    european_approach_is_permitted = PermissionTypeSerializer()
    ehea_key_commitment = PermissionTypeSerializer()
    flag = FlagSerializer()
    qa_requirements = CountryQARequirementReadSerializer(many=True, source='countryqarequirement_set')
    qaa_regulations = CountryQAARegulationSerializer(many=True, source='countryqaaregulation_set')

    class Meta:
        model = Country
        fields = '__all__'


class CountryWriteSerializer(WritableNestedModelSerializer):
    qa_requirements = CountryQARequirementWriteSerializer(many=True, source='countryqarequirement_set')
    qaa_regulations = CountryQAARegulationSerializer(many=True, source='countryqaaregulation_set')

    class Meta:
        model = Country
        fields = '__all__'