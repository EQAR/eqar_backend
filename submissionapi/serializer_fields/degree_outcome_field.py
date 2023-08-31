from rest_framework import serializers

from lists.models import DegreeOutcome


ACCEPTED_FULL_DEGREE_VALUES = [
    1, "1", 'yes', 'full degree'
]

ACCEPTED_NOT_FULL_DEGREE_VALUES = [
    2, "2", 'no', 'no full degree'
]


class DegreeOutcomeField(serializers.Field):
    def to_internal_value(self, data):
        if data not in ACCEPTED_FULL_DEGREE_VALUES and data not in ACCEPTED_NOT_FULL_DEGREE_VALUES:
            raise serializers.ValidationError("Please provide valid degree_outcome value.")
        else:
            if data in ACCEPTED_FULL_DEGREE_VALUES:
                degree_outcome = DegreeOutcome.objects.get(pk=1)
            else:
                degree_outcome = DegreeOutcome.objects.get(pk=2)
            return degree_outcome
