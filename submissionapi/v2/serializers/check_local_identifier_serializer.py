from rest_framework import serializers

from submissionapi.serializer_fields.agency_field import AgencyField


class CheckLocalIdentifierSerializer(serializers.Serializer):
    agency = AgencyField(required=True, label='Identifier or the acronym of the agency',
                         help_text='examples: "33", "ACQUIN"')
    local_identifier = serializers.CharField(
        max_length=255, required=True, label='Local identifier of the report', help_text='example: "QAA1153-March15"'
    )
