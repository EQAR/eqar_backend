from rest_framework import serializers

from datetime import datetime

class UnixTimestampDateField(serializers.Field):

    def to_internal_value(self, data):
        return date.fromtimestamp(data)

    def to_representation(self, value):
        return int(datetime.combine(value, datetime.min.time()).timestamp())

