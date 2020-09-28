from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from adminapi.serializers.flag_serializers import ReportFlagSerializer
from reports.models import ReportFlag


class ReportFlagList(generics.ListAPIView):
    serializer_class = ReportFlagSerializer
    filter_backends = (OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ['flag']
    ordering = ['-updated_at', 'created_at', 'report']
    search_fields = ['flag_message']
    queryset = ReportFlag.objects.filter(active=True)
