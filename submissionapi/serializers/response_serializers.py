from rest_framework import serializers

from institutions.models import Institution
from programmes.models import Programme
from reports.models import Report, ReportFile
from submissionapi.serializers.submisson_serializers import SubmissionPackageSerializer


class InstitutionSerializer(serializers.ModelSerializer):
    eter_id = serializers.SlugRelatedField(slug_field='eter_id', read_only=True, source='eter')

    class Meta:
        model = Institution
        fields = ('id', 'deqar_id', 'eter_id', 'name_primary')


class ProgrammeSerializer(serializers.ModelSerializer):
    countries = serializers.StringRelatedField(many=True)

    class Meta:
        model = Programme
        fields = ('id', 'name_primary', 'countries')


class ReportFileSerializer(serializers.ModelSerializer):
    report_language = serializers.StringRelatedField(many=True, source='languages')

    class Meta:
        model = ReportFile
        fields = ('id', 'file_display_name', 'file_original_location', 'file', 'report_language')


class ReportResponseSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()
    agency_esg_activity = serializers.StringRelatedField()
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    files = ReportFileSerializer(many=True, source='reportfile_set')
    institutions = InstitutionSerializer(many=True)
    programmes = ProgrammeSerializer(many=True, source='programme_set')

    class Meta:
        model = Report
        fields = ('id', 'agency', 'local_identifier', 'agency_esg_activity', 'name', 'status', 'decision',
                  'valid_from', 'valid_to', 'files', 'institutions', 'programmes')


class ReportSubmissionSuccessResponseSerializer(serializers.Serializer):
    submission_status = serializers.CharField(default="success")
    submitted_report = ReportResponseSerializer()
    sanity_check_status = serializers.ChoiceField(choices=["success", "warnings"])
    report_flag = serializers.ChoiceField(choices=["none", "low level", "high level"])
    report_warnings = serializers.CharField()
    institution_warnings = serializers.CharField()


class FieldErrorSerializer(serializers.Serializer):
    field = serializers.CharField()
    error = serializers.CharField()


class ReportSubmissionErrorResponseSerializer(serializers.Serializer):
    submission_status = serializers.CharField(default="error")
    original_data = SubmissionPackageSerializer()
    errors = FieldErrorSerializer(many=True)



