import io

import PyPDF2
from drf_extra_fields.fields import Base64FileField
from rest_framework import serializers


class PDFBase64File(Base64FileField):
    ALLOWED_TYPES = ['pdf']

    def get_file_extension(self, filename, decoded_file):
        try:
            PyPDF2.PdfFileReader(io.BytesIO(decoded_file))
        except PyPDF2.utils.PdfReadError as e:
            raise serializers.ValidationError("File is not a valid pdf file")
        else:
            return 'pdf'
