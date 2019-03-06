from django.test import TestCase
from submissionapi.populators.populator import Populator
from django.contrib.auth.models import User


class PopulatorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser',
                                                  email='testuser@eqar.eu',
                                                  password='testpassword')
        self.user.save()

    def test_init(self):
        populator = Populator(data={'agency': '1'}, user=self.user)
        self.assertEqual(populator.data['agency'], "1")
