from rest_framework import serializers


class DateBlankSerializer(serializers.DateField):
    def to_internal_value(self, data):
        if data == '':
            return None
        else:
            return super(DateBlankSerializer, self).to_internal_value(data)