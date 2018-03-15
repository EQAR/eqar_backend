from django_filters.rest_framework import filters
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from adminapi.serializers.institution_serializer import InstitutionSelectListSerializer
from institutions.models import Institution


class InstitutionSelectList(generics.ListAPIView):
    serializer_class = InstitutionSelectListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name_primary',)
    ordering = ('name_primary',)
    queryset = Institution.objects.all().order_by('name_primary')