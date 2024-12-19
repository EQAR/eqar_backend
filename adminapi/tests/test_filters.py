from django.test import TestCase
from django.db import models
from rest_framework.test import APIRequestFactory
from ..filters import CaseInsensitiveOrderingFilter

# FILE: adminapi/test_filters.py


# Test model
class TestModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

class CaseInsensitiveOrderingFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        TestModel.objects.create(name='apple')
        TestModel.objects.create(name='Banana')
        TestModel.objects.create(name='cherry')

    def setUp(self):
        self.factory = APIRequestFactory()
        self.filter = CaseInsensitiveOrderingFilter()

    def test_ordering_asc(self):
        request = self.factory.get('/test', {'ordering': 'name'})
        queryset = TestModel.objects.all()
        filtered_queryset = self.filter.filter_queryset(request, queryset, None)
        self.assertEqual(list(filtered_queryset.values_list('name', flat=True)), ['apple', 'Banana', 'cherry'])

    def test_ordering_desc(self):
        request = self.factory.get('/test', {'ordering': '-name'})
        queryset = TestModel.objects.all()
        filtered_queryset = self.filter.filter_queryset(request, queryset, None)
        self.assertEqual(list(filtered_queryset.values_list('name', flat=True)), ['cherry', 'Banana', 'apple'])