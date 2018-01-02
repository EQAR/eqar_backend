from rest_framework import serializers
from reports.models import Report, ReportFile
from webapi.serializers.agency_serializers import AgencyESGActivitySerializer
from webapi.serializers.institution_serializers import InstitutionListSerializer
from webapi.serializers.programme_serializers import ProgrammeSerializer


class ReportFileSerializer(serializers.ModelSerializer):
    languages = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ReportFile
        fields = ['file_name', 'file', 'languages']


class ReportListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="webapi-v1:report-detail")
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:agency-detail",
                                                     source='agency')
    agency_name = serializers.StringRelatedField(source='agency')
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    institution_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:institution-detail",
                                                          source='institution_id')
    institution_name_primary = serializers.CharField(required=False)
    programme_name_primary = serializers.CharField(required=False)

    class Meta:
        model = Report
        fields = ['url', 'name', 'valid_from', 'report_files',
                  'agency_name', 'agency_url', 'institution_name_primary', 'institution_url', 'programme_name_primary']


class ReportDetailSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()
    agency_url = serializers.HyperlinkedRelatedField(read_only=True, view_name="webapi-v1:agency-detail",
                                                     source='agency')
    institutions = InstitutionListSerializer(many=True, read_only=True)
    programmes = ProgrammeSerializer(many=True, read_only=True, source='programme_set')
    report_files = ReportFileSerializer(many=True, read_only=True, source='reportfile_set')
    agency_esg_activity = AgencyESGActivitySerializer()
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()

    class Meta:
        model = Report
        fields = ['id', 'local_identifier', 'name', 'valid_from', 'valid_to',
                  'agency', 'agency_url',
                  'institutions', 'programmes',
                  'agency_esg_activity', 'status', 'decision',
                  'report_files']
