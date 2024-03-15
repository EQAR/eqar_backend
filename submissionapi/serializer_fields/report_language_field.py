import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lists.models import Language


class ReportLanguageField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        if len(data) == 2:
            try:
                language = Language.objects.get(iso_639_1__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid language code.")
        elif len(data) == 3:
            try:
                language = Language.objects.get(iso_639_2__iexact=data)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid language code.")
        else:
            raise serializers.ValidationError("Please provide valid language code.")
        return language

