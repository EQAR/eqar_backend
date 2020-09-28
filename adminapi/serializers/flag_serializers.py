from rest_framework import serializers

from agencies.models import Agency
from reports.models import ReportFlag


class ReportFlagSerializer(serializers.ModelSerializer):
    agency = serializers.SlugRelatedField(source='report.agency', slug_field='acronym_primary',
                                          queryset=Agency.objects.all())
    flag = serializers.StringRelatedField()
    institution_programme_primary = serializers.SerializerMethodField()

    def get_institution_programme_primary(self, obj):
        institutions = []
        programmes = []

        for inst in obj.report.institutions.iterator():
            institutions.append(inst.name_primary)

        for programme in obj.report.programme_set.iterator():
            programmes.append(programme.name_primary)

        institutions = "; ".join(institutions)
        programmes = " / ".join(programmes)

        if len(programmes) > 0:
            return "%s - %s" % (institutions, programmes)
        else:
            return institutions

    class Meta:
        model = ReportFlag
        fields = '__all__'
