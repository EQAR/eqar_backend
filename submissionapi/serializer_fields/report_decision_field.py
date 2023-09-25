import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from reports.models import ReportDecision


class ReportDecisionField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                decision = ReportDecision.objects.get(pk=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Decision ID.")
        else:
            try:
                decision = ReportDecision.objects.get(decision__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Decision.")
        return decision