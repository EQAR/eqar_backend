from drf_writable_nested import WritableNestedModelSerializer, UniqueFieldsMixin
from rest_framework import serializers

from adminapi.serializers.select_serializers import QFEHEALevelSelectSerializer, CountrySelectSerializer
from programmes.models import Programme, ProgrammeName


class ProgrammeAlternativeNameSerializer(UniqueFieldsMixin, serializers.ModelSerializer):
    name_alternative = serializers.CharField(max_length=200, source='name', required=False)
    qualification_alternative = serializers.CharField(max_length=200, source='qualification',
                                                      allow_blank=True, required=False)

    class Meta:
        model = ProgrammeName
        fields = ['id', 'name_alternative', 'qualification_alternative', 'name_is_primary']


class ProgrammeReadSerializer(serializers.ModelSerializer):
    alternative_names = ProgrammeAlternativeNameSerializer(many=True, required=False, source='programmename_set')
    qf_ehea_level = QFEHEALevelSelectSerializer(required=False, allow_null=True)
    countries = CountrySelectSerializer(many=True)

    class Meta:
        model = Programme
        fields = ['id', 'alternative_names', 'nqf_level', 'qf_ehea_level', 'countries']


class ProgrammeWriteSerializer(WritableNestedModelSerializer):
    alternative_names = ProgrammeAlternativeNameSerializer(many=True, required=False, source='programmename_set')

    class Meta:
        model = Programme
        fields = ['id', 'alternative_names', 'nqf_level', 'qf_ehea_level', 'countries']