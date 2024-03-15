import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lists.models import Assessment


class AssessmentField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                assessment = Assessment.objects.get(id=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Assessment ID.")
        else:
            try:
                assessment = Assessment.objects.get(assessment__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid assessment name.")

        return assessment
