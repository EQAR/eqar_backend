import json

import requests
from rest_framework.views import APIView


class SyncETERView(APIView):
    def get(self, request, format=None):
        """
        Sync ETER entries with DEQAR.
        """

        payload = {"BAS.REFYEAR.v": {"$in": [2014]}}
        r = requests.post('https://www.eter-project.com/api/eter/HEIs/filter', data=json.dumps(payload))
        r.status_code