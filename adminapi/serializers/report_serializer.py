from rest_framework import serializers
from reports.models import Report


class ReportDashboardSerializer(serializers.ModelSerializer):
    institutions = serializers.StringRelatedField(many=True)
    programmes = serializers.StringRelatedField(many=True, source='programme_set')
    flag = serializers.StringRelatedField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'name', 'institutions', 'programmes', 'flag', 'date']

    def get_date(self, obj):
        logs = obj.submissionlog_set.latest('submission_date')
        if logs:
            return logs.submission_date
        else:
            return None
