from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from submissionapi.v1.closure import SUBMISSION_V1_CLOSED_MESSAGE


class SubmissionAPIV1ReportTest(APITestCase):
    def setUp(self):
        self.valid_data = {
            "agency": "ACQUIN",
            "valid_from": "2010-05-05",
            "date_format": "%Y-%M-%d",
            "activity": "1",
            "status": "1",
            "decision": "1",
            "report_files": [
                {
                    "report_language": ["eng"]
                }
            ],
            "institutions": [
                {
                    "eter_id": "DE0392",
                    "identifiers": [
                        {
                            "identifier": "LOCAL001",
                            "resource": "local identifier"
                        }, {
                            "identifier": "DE0876",
                            "resource": "national identifier"
                        }
                    ]
                }
            ],
            "programmes": [
                {
                    "name_primary": "Programme name"
                }
            ]
        }
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@eqar.eu',
                                             password='testpassword')
        self.user.save()
        self.token = Token.objects.get(user__username='testuser')

    def test_closure_submission(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post(
            '/submissionapi/v1/submit/report',
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, 410, response.data)
        self.assertEqual(response.data['detail'], SUBMISSION_V1_CLOSED_MESSAGE)

    def test_closure_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.delete('/submissionapi/v1/delete/report/2/')
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.data['detail'], SUBMISSION_V1_CLOSED_MESSAGE)
