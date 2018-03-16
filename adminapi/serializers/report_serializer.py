from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from reports.models import Report


class ReportDashboardSerializer(serializers.ModelSerializer):
    agency = serializers.SlugRelatedField(read_only=True, slug_field='acronym_primary')
    institutions = serializers.StringRelatedField(many=True)
    programmes = serializers.StringRelatedField(many=True, source='programme_set')
    flag = serializers.StringRelatedField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'agency', 'name', 'institutions', 'programmes', 'flag', 'date']

    def get_date(self, obj):
        try:
            logs = obj.submissionreportlog_set.latest('submission_date')
            if logs:
                return logs.submission_date
            else:
                return None
        except ObjectDoesNotExist:
            return None

