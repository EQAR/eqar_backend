import re
from rest_framework.serializers import ValidationError
from eqar_backend.serializer_fields.esco_serializer_field import ESCOSerializer


class ISCEDSerializer(ESCOSerializer):
    def to_internal_value(self, data):
        if data == '':
            return None
        else:
            isced_data = data

            # If submitted data is not an ESCO URI.
            if 'http://data.europa.eu/esco/isced-f' not in isced_data:
                # Check if data is a maximum 4-digit code
                if not re.search("^[0-9]{1,4}$", isced_data):
                    raise ValidationError('Either full ESCO URI or '
                                          'max. 4-digit ISCED-F number needed.')
                else:
                    isced_data = 'http://data.europa.eu/esco/isced-f/%s' % isced_data

            return super(ISCEDSerializer, self).to_internal_value(isced_data)

    def to_representation(self, instance):
        return super(ISCEDSerializer, self).to_representation(instance)
