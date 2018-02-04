from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from submissionapi.serializers import SubmissionPackageSerializer


class Submission(APIView):
    def post(self, request, format=None):
        serializer = SubmissionPackageSerializer(data=request.data)
        if serializer.is_valid():
            # Do the logic here
            pass
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
