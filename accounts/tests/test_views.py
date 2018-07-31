from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AccountsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()

    def test_get_token_success(self):
        """
            Test if we can display a token.
        """
        response = self.client.post('/accounts/get_token/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.data['state'], 'success')

    def test_get_token_wront_credentials(self):
        """
            Test if we can display an error.
        """
        response = self.client.post('/accounts/get_token/', {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.data['state'], 'error')

    def test_create_token_success(self):
        """
            Test if we can create a token.
        """
        response = self.client.post('/accounts/get_token/', {'username': 'testuser', 'password': 'testpassword'})
        token_old = response.data['token']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token_old)
        response = self.client.post('/accounts/get_new_token/')
        token_new = response.data['token']
        self.assertTrue(len(token_old) == 40)
        self.assertTrue(len(token_new) == 40)
        self.assertTrue(token_new != token_old)

    def test_change_email_valid(self):
        """
            Test if we can change an email address.
        """
        self.token = Token.objects.get(user__username='testuser')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post('/accounts/change_email/', {'new_email': 'example@example.com',
                                                                're_new_email': 'example@example.com'})
        self.assertEqual(response.data['email'], 'example@example.com')

    def test_change_email_invalid(self):
        """
            Test if we can't change an email address with bad data.
        """
        self.token = Token.objects.get(user__username='testuser')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.post('/accounts/change_email/', {'new_email': 'example@example.com',
                                                                're_new_email': 'example2@example2.com'})
        self.assertEqual(response.data['error']['non_field_errors'][0], 'Please provide identical e-mail addresses.')
