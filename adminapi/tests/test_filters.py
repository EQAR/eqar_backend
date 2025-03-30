from django.test import TestCase, RequestFactory
from drf_rw_serializers.generics import ListAPIView
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.settings import api_settings
from django.db import models
from ..filters import CaseInsensitiveOrderingFilter
from lists.models import Flag
from rest_framework.request import Request

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = ['flag']

class TestView(ListAPIView):
    permission_classes = []
    authentication_classes = []
    pagination_class = None
    queryset = Flag.objects.all()
    filter_backends = (CaseInsensitiveOrderingFilter,)
    serializer_class = TestSerializer

class CaseInsensitiveOrderingFilterTest(TestCase):
    fixtures = ['flag']

    def setUp(self):
        self.factory = APIRequestFactory()
        self.filter = CaseInsensitiveOrderingFilter()
        Flag.objects.create(flag='A first flag')
        
    def test_ordering_asc(self):
        request = self.factory.get('/test', {'ordering': 'flag'})
        view = TestView.as_view()
        response = view(request)
        self.assertEqual(
            response.data[0]['flag'],
            'A first flag'
        )
        self.assertEqual(
            response.data[1]['flag'],
            'high level'
        )

    def test_ordering_desc(self):
        request = self.factory.get('/test', {'ordering': '-flag'})
        view = TestView.as_view()
        response = view(request)
        self.assertEqual(
            response.data[0]['flag'],
            'none'
        )
        self.assertEqual(
            response.data[1]['flag'],
            'low level'
        )