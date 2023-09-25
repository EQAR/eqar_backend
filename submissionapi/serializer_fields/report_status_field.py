import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from reports.models import ReportStatus


class ReportStatusField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                status = ReportStatus.objects.get(pk=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Status ID.")
        else:
            try:
                status = ReportStatus.objects.get(status__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Report Status.")
        return status
