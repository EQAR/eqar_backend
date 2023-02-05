import json

from django.conf import settings

from rest_framework.renderers import BaseRenderer
from rest_framework.exceptions import NotAcceptable

class JWTRenderer(BaseRenderer):
    """
    Hardly a real renderer, simply return JWT string
    """
    format = 'jwt'
    media_type = 'application/jwt'

    def render(self, data, media_type=None, renderer_context={}):
        if not isinstance(data, str):
            raise NotAcceptable()
        return(data)

