from rest_framework import generics

from adminapi.serializers.institution_serializers import InstitutionSerializer
from institutions.models import Institution


class InstitutionDetail(generics.RetrieveUpdateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer


class InstitutionCreate(generics.CreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
