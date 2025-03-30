import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from reports.models import Report


class ReportIdentifierPlusIntegerField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type) and not isinstance(data, six.integer_types):
            msg = 'Incorrect type. Expected a string or integer, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        try:
            report = Report.objects.get(id=data)

            user = self.context['request'].user
            submitting_agency = user.deqarprofile.submitting_agency

            if not submitting_agency.agency_allowed(report.agency):
                raise serializers.ValidationError("You are not allowed to submit data to this Report.")

        except ObjectDoesNotExist:
            raise serializers.ValidationError("Please provide valid Report ID.")
        return report