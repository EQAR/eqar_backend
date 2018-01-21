import datetime
from django.db.models import Q
from rest_framework import serializers


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