import io

from bs4 import UnicodeDammit
from rest_framework.parsers import BaseParser


class CSVParser(BaseParser):
    """
    CSV parser.
    """
    media_type = 'text/csv'

    def parse(self, stream, media_type=None, parser_context=None):
        dammit = UnicodeDammit(stream.read())
        return dammit.unicode_markup
