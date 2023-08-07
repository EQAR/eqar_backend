from rest_framework import serializers
from rest_framework.serializers import ValidationError
import requests


class ESCOSerializer(serializers.CharField):
    def to_internal_value(self, data):
        if data == '':
            return None
        else:
            # Check if data has the format of ESCO URIs
            if 'http://data.europa.eu/esco/' not in data:
                raise ValidationError('ESCO base URL is missing from the data.')
            return super(ESCOSerializer, self).to_internal_value(data)

    def to_representation(self, instance):
        # Resolve ESCO URI
        r = requests.get(
            'https://ec.europa.eu/esco/api/resource/skill',
            params={'uri': instance}
        )
        if r.status_code == 200:
            j = r.json()
            data = {'uri': instance, 'title': j['title']}
        else:
            data = {'uri': instance}
        return super(ESCOSerializer, self).to_representation(data)
