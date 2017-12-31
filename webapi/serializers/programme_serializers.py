from rest_framework import serializers
from programmes.models import Programme, ProgrammeName


class ProgrammeNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeName
        fields = ['name', 'name_is_english', 'qualification']


class ProgrammeSerializer(serializers.ModelSerializer):
    names = ProgrammeNameSerializer(many=True, read_only=True, source='programmename_set')
    countries = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Programme
        fields = ['names', 'nqf_level', 'qf_ehea_level', 'countries']