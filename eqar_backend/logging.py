import logging

from rest_framework import status

class SkipHttp503Errors(logging.Filter):
    """
    filter out errors resulting from a 503 Service Unavailable response
    (to prevent emails being sent to admins)
    """

    def filter(self, record):
        if getattr(record, 'status_code', None) == status.HTTP_503_SERVICE_UNAVAILABLE:
            return False
        else:
            return True

