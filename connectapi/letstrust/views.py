import json
import datetime

import requests
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView
from django.conf import settings

from institutions.models import InstitutionIdentifier
from reports.models import Report


class VCIssue(APIView):
    def get(self, request, *args, **kwargs):
        return Response({})
