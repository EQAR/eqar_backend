import six
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from countries.models import Country


class CountryField(serializers.Field):
    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise serializers.ValidationError(msg % type(data).__name__)

        country = data.upper()
        if len(country) == 2:
            try:
                c = Country.objects.get(iso_3166_alpha2__iexact=country)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid country code.")
        elif len(country) == 3:
            try:
                c= Country.objects.get(iso_3166_alpha3__iexact=country)
            except ObjectDoesNotExist:
                raise serializers.ValidationError("Please provide valid country code.")
        else:
            raise serializers.ValidationError("Please provide valid country code.")
        return c