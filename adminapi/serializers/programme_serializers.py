from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from programmes.models import Programme


class ProgrammeSerializer(WritableNestedModelSerializer):


    class Meta:
        model = Programme
        fields = ['id', 'name_primary', 'nqf_level', 'qf_ehea_level', 'countries']
