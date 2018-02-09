from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from submissionapi.serializers import SubmissionPackageSerializer


class Submission(APIView):
    def post(self, request, format=None):
        # Check if request is a list:
        if isinstance(request.data, list):
            response_list = []
            response_contains_error = False

            for data in request.data:
                serializer = SubmissionPackageSerializer(data=data)
                if serializer.is_valid():
                    # Do the logic here
                    response_list.append(self.make_success_response(serializer))
                else:
                    response_contains_error = True
                    response_list.append(self.make_error_response(serializer,data))

            if response_contains_error:
                return Response(response_list, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(response_list, status=status.HTTP_200_OK)

        # If request is not a list
        else:
            serializer = SubmissionPackageSerializer(data=request.data)
            if serializer.is_valid():
                # Do the logic here
                return Response(self.make_success_response(serializer), status=status.HTTP_200_OK)
            else:
                return Response(self.make_error_response(serializer, request.data), status=status.HTTP_400_BAD_REQUEST)

    def make_success_response(self, serializer):
        return {
            'submission_status': 'success',
            'sanity_check_status': '',
            'sanity_check_warnings': ''
        }

    def make_error_response(self, serializer, original_data):
        return {
            'submission_status': 'errors',
            'original_data': original_data,
            'errors': serializer.errors
        }