from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpRequest, QueryDict
from rest_framework.request import Request


class PublicHttpRequest(HttpRequest):
    """
    Stand-in request for using the Web API serializers outside a request/response cycle: absolute URLs (e.g. of
    report files) are built against MCP_PUBLIC_BASE_URL.
    """

    def __init__(self, query):
        super().__init__()
        base_url = urlsplit(settings.MCP_PUBLIC_BASE_URL)
        self._public_scheme = base_url.scheme
        self._public_host = base_url.netloc
        self.method = 'GET'
        self.path = self.path_info = '/'
        self.GET = QueryDict(mutable=True)
        for key, value in query.items():
            if value is not None:
                self.GET[key] = value

    def get_host(self):
        # bypasses ALLOWED_HOSTS validation, as the host is not client-supplied
        return self._public_host

    def _get_scheme(self):
        return self._public_scheme


def public_request(**query):
    """
    DRF request to pass as serializer context; query holds parameters some serializers read, e.g. history='true'
    """
    return Request(PublicHttpRequest(query))
