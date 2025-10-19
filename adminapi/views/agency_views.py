import os

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_filters import rest_framework as filters
from drf_rw_serializers.generics import RetrieveUpdateAPIView, CreateAPIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from adminapi.permissions import CanAccessAgency
from adminapi.serializers.agency_serializers import AgencyReadSerializer, \
    AgencyUserWriteSerializer, AgencyAdminWriteSerializer, AgencyActivityGroupWriteSerializer, \
    AgencyActivityGroupReadSerializer
from adminapi.serializers.select_serializers import AgencyESGActivitySerializer
from agencies.models import Agency, AgencyActivityType, AgencyESGActivity, AgencyEQARDecision, AgencyUpdateLog, \
    AgencyActivityGroup
from submissionapi.permissions import CanSubmitToAgency


class AgencyESGActivityFilterClass(filters.FilterSet):
    agency = filters.ModelChoiceFilter(field_name='agency', queryset=Agency.objects.all())
    activity = filters.CharFilter(label='Activity', method='search_activity')
    activity_id = filters.CharFilter(label='Agency ID', method='search_activity_id')
    activity_type = filters.ModelChoiceFilter(field_name='activity_group__activity_type', queryset=AgencyActivityType.objects.all())
    activity_group = filters.ModelChoiceFilter(field_name='activity_group', queryset=AgencyActivityGroup.objects.all())

    def search_activity(self, queryset, name, value):
        return queryset.filter(activity__icontains=value)

    def search_activity_id(self, queryset, name, value):
        if value.isnumeric():
            return queryset.filter(id=value)
        else:
            return AgencyESGActivity.objects.none()

    class Meta:
        model = AgencyESGActivity
        fields = ['agency', 'activity', 'activity_type', 'activity_id']


class AgencyESGActivityList(generics.ListAPIView):
    serializer_class = AgencyESGActivitySerializer
    filter_backends = (OrderingFilter, filters.DjangoFilterBackend)
    ordering = ['agency__acronym_primary', 'id', 'activity_group']
    filterset_class = AgencyESGActivityFilterClass
    queryset = AgencyESGActivity.objects.all()


class AgencyDetail(RetrieveUpdateAPIView):
    queryset = Agency.objects.all()
    read_serializer_class = AgencyReadSerializer
    write_serializer_class = AgencyAdminWriteSerializer

    def get_permissions(self):
        if self.request.method == 'PUT':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(responses={'200': AgencyReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(AgencyDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=AgencyAdminWriteSerializer, responses={'200': AgencyReadSerializer})
    def put(self, request, *args, **kwargs):
        agency = Agency.objects.get(id=kwargs.get('pk'))

        submit_comment = request.data.get('submit_comment', None)
        if submit_comment:
            AgencyUpdateLog.objects.create(
                agency=agency,
                note=submit_comment,
                updated_by=request.user
            )
        else:
            AgencyUpdateLog.objects.create(
                agency=agency,
                note='Agency updated',
                updated_by=request.user
            )

        agency.save()
        return super(AgencyDetail, self).put(request, *args, **kwargs)


class MyAgencyDetail(RetrieveUpdateAPIView):
    queryset = Agency.objects.all()
    read_serializer_class = AgencyReadSerializer
    write_serializer_class = AgencyUserWriteSerializer
    permission_classes = (CanAccessAgency|IsAdminUser,)

    @swagger_auto_schema(responses={'200': AgencyReadSerializer})
    def get(self, request, *args, **kwargs):
        return super(MyAgencyDetail, self).get(request, *args, **kwargs)

    @swagger_auto_schema(request_body=AgencyUserWriteSerializer, responses={'200': AgencyReadSerializer})
    def put(self, request, *args, **kwargs):
        agency = Agency.objects.get(id=kwargs.get('pk'))

        submit_comment = request.data.get('submit_comment', None)
        if submit_comment:
            AgencyUpdateLog.objects.create(
                agency=agency,
                note=submit_comment,
                updated_by=request.user
            )
        else:
            AgencyUpdateLog.objects.create(
                agency=agency,
                note='Agency updated',
                updated_by=request.user
            )

        agency.save()
        return super(MyAgencyDetail, self).put(request, *args, **kwargs)


class AgencyDecisionFileUploadView(APIView):
    """
        Responsible for the submission of agency decision files
    """
    parser_classes = (FileUploadParser,)
    permission_classes = (CanSubmitToAgency|IsAdminUser,)
    swagger_schema = None

    def put(self, request, filename, pk, file_type, format=None):
        file_obj = request.data['file']
        try:
            agency_decision = AgencyEQARDecision.objects.get(pk=pk)
            file_path = os.path.join(settings.MEDIA_ROOT, 'EQAR', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            if file_type == 'decision':
                agency_decision.decision_file.name = os.path.join('EQAR', filename)
            if file_type == 'decision_extra':
                agency_decision.decision_file_extra.name = os.path.join('EQAR', filename)
            agency_decision.save()

            return Response(status=204)
        except ObjectDoesNotExist:
            return Response(status=404)


class AgencyActivityGroupCreateView(CreateAPIView):
    queryset = AgencyActivityGroup.objects.all()
    read_serializer_class = AgencyActivityGroupReadSerializer
    write_serializer_class = AgencyActivityGroupWriteSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class AgencyActivityGroupUpdateView(RetrieveUpdateAPIView):
    queryset = AgencyActivityGroup.objects.all()
    read_serializer_class = AgencyActivityGroupReadSerializer
    write_serializer_class = AgencyActivityGroupWriteSerializer

    def get_permissions(self):
        if self.request.method == 'PUT':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
