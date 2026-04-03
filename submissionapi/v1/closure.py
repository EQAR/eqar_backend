from rest_framework import status
from rest_framework.response import Response

SUBMISSION_V1_CLOSED_MESSAGE = (
    "Submission API v1 endpoints are closed. "
    "From April 6, 2026, please use Submission API v2 endpoints."
)


def submission_v1_closed_response():
    return Response(
        data={"detail": SUBMISSION_V1_CLOSED_MESSAGE},
        status=status.HTTP_410_GONE,
    )
