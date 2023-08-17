import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lists.models import DegreeOutcome


class DegreeOutcomeField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                degree_outcome = DegreeOutcome.objects.get(code=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Degree Outcome ID.")
        else:
            try:
                degree_outcome = DegreeOutcome.objects.get(outcome__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Degree Outcome description.")
        return degree_outcome
