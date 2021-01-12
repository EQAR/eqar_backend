"""
Provides XML rendering support.
"""
from dict2xml import dict2xml
from lxml import etree
from rest_framework.renderers import BaseRenderer


class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    """

    media_type = "application/xml"
    format = "xml"
    charset = "utf-8"
    item_tag_name = "list-item"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ""

        if isinstance(data, dict):
            return dict2xml(data)
        else:
            return etree.tostring(data, pretty_print=True)
