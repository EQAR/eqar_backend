

from rest_framework import generics

from agencies.models import Agency
from discovery_api.serializers.agency_serializers import AgencyListSerializer, AgencyDetailSerializer


class AgencyList(generics.ListAPIView):
    queryset = Agency.objects.all().order_by()
    serializer_class = AgencyListSerializer


class AgencyDetail(generics.RetrieveAPIView):
    queryset = Agency.objects.all()
    serializer_class = AgencyDetailSerializer
