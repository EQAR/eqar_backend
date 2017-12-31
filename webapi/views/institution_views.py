from django.db.models import Q
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from institutions.models import Institution
from reports.models import Report
from webapi.serializers.institution_serializers import InstitutionListSerializer, InstitutionDetailSerializer


class InstitutionList(generics.ListAPIView):
    """
        Returns a list of all the institutions to which report was submitted in DEQAR.
    """
    serializer_class = InstitutionListSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name_primary',)
    ordering = ('name_primary',)

    def get_queryset(self):
        return Institution.objects.filter(reports__isnull=False).distinct()


class InstitutionDetail(generics.RetrieveAPIView):
    """
        Returns all the data available of the selected institution.
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionDetailSerializer


class InstitutionListByCountry(InstitutionList):
    """
        Returns a list of all the institutions in DEQAR based in the submitted country.
    """
    def get_queryset(self):
        return Institution.objects.filter(Q(institutioncountry__country=self.kwargs['country']))


class InstitutionListByAgency(InstitutionList):
    """
        Returns a list of all the institutions in DEQAR based in the submitted agency.
    """
    def get_queryset(self):
        return Institution.objects.filter(reports__agency=self.kwargs['agency']).distinct()
