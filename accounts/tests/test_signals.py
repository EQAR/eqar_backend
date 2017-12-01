from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token


class AccountSignalTestCase(TestCase):
    """
    Test module for the signals in Accounts app.
    """
    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()

    def test_if_token_was_created(self):
        """
            Test if token was created for testuser.
        """
        token = Token.objects.get(user__username='testuser')
        self.assertEqual(len(token.key), 40)
