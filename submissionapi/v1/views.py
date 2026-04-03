from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from submissionapi.v1.closure import SUBMISSION_V1_CLOSED_MESSAGE, submission_v1_closed_response


class ClosureView(APIView):
    permission_classes = (AllowAny,)
    swagger_schema = None

    def post(self, request):
        return submission_v1_closed_response()

    def put(self, request):
        return submission_v1_closed_response()

    def delete(self, request, *args, **kwargs):
        return submission_v1_closed_response()