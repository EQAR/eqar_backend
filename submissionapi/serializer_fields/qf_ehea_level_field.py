import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lists.models import QFEHEALevel


class QFEHEALevelField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                qf_ehea_level = QFEHEALevel.objects.get(code=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid QF EHEA ID.")
        else:
            try:
                qf_ehea_level = QFEHEALevel.objects.get(level__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid QF EHEA level.")
        return qf_ehea_level

