import datetime
from django.db.models import Q
from rest_framework import serializers

from institutions.models import InstitutionIdentifier


class HistoryFilteredListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        fields = [f.name for f in data.model._meta.get_fields()]
        valid_field = [s for s in fields if "valid_to" in s][0]

        include_history = self.context['request'].query_params.get('history', None)

        if include_history == 'true':
            data = data.all()
        else:
            data = data.filter(
                Q(**{"%s__isnull" % valid_field: True}) | Q(**{"%s__gt" % valid_field: datetime.datetime.now()})
            )
        return super(HistoryFilteredListSerializer, self).to_representation(data)


class InstitutionIdentifierTypeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        t = self._context.get('type', None)
        if t == 'local':
            data = data.filter(resource='local identifier')
        if t == 'national':
            data = data.exclude(resource='local identifier')
        return super(InstitutionIdentifierTypeSerializer, self).to_representation(data)


class InstitutionNameTypeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        t = self._context.get('type', None)
        if t == 'actual':
            data = data.filter(name_valid_to__isnull=True)
        else:
            data = data.filter(name_valid_to__isnull=False)
        return super(InstitutionNameTypeSerializer, self).to_representation(data)


class AgencyNameTypeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        t = self._context.get('type', None)
        if t == 'actual':
            data = data.filter(name_valid_to__isnull=True)
        else:
            data = data.filter(name_valid_to__isnull=False)
        return super(AgencyNameTypeSerializer, self).to_representation(data)
