from django.conf.urls import url
from submissionapi.views import Submission

urlpatterns = [
    url(r'^submit/report$', Submission.as_view(), name='submit-report')
]
