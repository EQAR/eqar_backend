import io

from drf_extra_fields.fields import Base64FileField
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from rest_framework import serializers


class PDFBase64File(Base64FileField):
    ALLOWED_TYPES = ['pdf']

    def get_file_extension(self, filename, decoded_file):
        try:
            PdfReader(io.BytesIO(decoded_file))
        except PdfReadError as e:
            raise serializers.ValidationError("File is not a valid pdf file")
        else:
            return 'pdf'
