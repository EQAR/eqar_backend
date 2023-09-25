import six
from rest_framework import serializers

ACCEPTED_TRUE_VALUES = [
    'Yes', 'yes', 'TRUE', 'True', 'true',
]

ACCEPTED_FALSE_VALUES = [
    'No', 'no', 'FALSE', 'False', 'false'
]


class BooleanExtendedField(serializers.BooleanField):
    def to_internal_value(self, data):
        if data == '':
            return None

        if not isinstance(data, bool):
            if not isinstance(data, six.text_type):
                msg = 'Incorrect type. Expected a string, but got %s'
                raise serializers.ValidationError(msg % type(data).__name__)

            if data not in ACCEPTED_TRUE_VALUES and data not in ACCEPTED_FALSE_VALUES:
                msg = 'Incorrect value. Only a boolean value, or yes/no, true/false pairs are allowed.'
                raise serializers.ValidationError(msg)

            if data in ACCEPTED_TRUE_VALUES:
                return True

            if data in ACCEPTED_FALSE_VALUES:
                return False
        else:
            return super(BooleanExtendedField, self).to_internal_value(data)