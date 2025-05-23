from rest_framework import serializers

from agencies.models import Agency
from institutions.models import Institution
from lists.models import DegreeOutcome
from programmes.models import Programme
from reports.models import Report, ReportFile

from submissionapi.v1.serializers.submisson_serializers import SubmissionPackageSerializer


class ResponseInstitutionSerializer(serializers.ModelSerializer):
    eter_id = serializers.SlugRelatedField(slug_field='eter_id', read_only=True, source='eter')

    class Meta:
        model = Institution
        fields = ('id', 'deqar_id', 'eter_id', 'name_primary')


class ResponseProgrammeSerializer(serializers.ModelSerializer):
    countries = serializers.StringRelatedField(many=True)
    degree_outcome = serializers.SlugRelatedField(slug_field='outcome', queryset=DegreeOutcome.objects.all())

    class Meta:
        model = Programme
        fields = ('id', 'name_primary', 'countries', 'degree_outcome')


class ResponseReportFileSerializer(serializers.ModelSerializer):
    report_language = serializers.StringRelatedField(many=True, source='languages')

    class Meta:
        model = ReportFile
        fields = ('id', 'file_display_name', 'file_original_location', 'file', 'report_language')


class ResponseCSVReportSerializer(serializers.ModelSerializer):
    report_id = serializers.IntegerField(source='id')

    class Meta:
        model = Report
        fields = ('report_id', )


class ResponseReportSerializer(serializers.ModelSerializer):
    agency = serializers.StringRelatedField()
    contributing_agencies = serializers.SlugRelatedField(many=True, slug_field="acronym_primary", queryset=Agency.objects.all())
    agency_esg_activity = serializers.SerializerMethodField()
    status = serializers.StringRelatedField()
    decision = serializers.StringRelatedField()
    files = ResponseReportFileSerializer(many=True, source='reportfile_set')
    institutions = ResponseInstitutionSerializer(many=True)
    programmes = ResponseProgrammeSerializer(many=True, source='programme_set')

    def get_agency_esg_activity(self, obj):
        activity = obj.agency_esg_activities.first()
        return str(activity) if activity else 'N/A'

    class Meta:
        model = Report
        fields = ('id', 'agency', 'contributing_agencies', 'local_identifier', 'agency_esg_activity', 'status',
                  'decision', 'summary', 'valid_from', 'valid_to', 'files', 'institutions', 'programmes')


class ResponseReportSuccessResponseSerializer(serializers.Serializer):
    submission_status = serializers.CharField(default="success")
    submitted_report = ResponseReportSerializer()
    sanity_check_status = serializers.ChoiceField(choices=["success", "warnings"])
    report_flag = serializers.ChoiceField(choices=["none", "low level", "high level"])
    report_warnings = serializers.ListField(child=serializers.CharField(allow_blank=True), min_length=0)
    institution_warnings = serializers.ListField(child=serializers.CharField(allow_blank=True), min_length=0)


class FieldErrorSerializer(serializers.Serializer):
    field = serializers.CharField()
    error = serializers.CharField()


class ResponseReportErrorResponseSerializer(serializers.Serializer):
    submission_status = serializers.CharField(default="error")
    original_data = SubmissionPackageSerializer()
    errors = FieldErrorSerializer(many=True)



