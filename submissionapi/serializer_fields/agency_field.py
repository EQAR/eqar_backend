import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from agencies.models import Agency


class AgencyField(serializers.Field):
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

        if 'request' in self.context:
            user = self.context['request'].user
            submitting_agency = user.deqarprofile.submitting_agency
            if not submitting_agency.agency_allowed(agency):
                raise serializers.ValidationError("You can't submit data to this Agency.")
            return agency
        else:
            return agency
