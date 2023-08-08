import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from agencies.models import Agency


class ContributingAgencyField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if data.isdigit():
            try:
                agency = Agency.objects.get(deqar_id=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency DEQAR ID.")
        else:
            try:
                agency = Agency.objects.get(acronym_primary__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid Agency Acronym.")

        return agency