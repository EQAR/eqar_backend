import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Report(models.Model):
    """
    List of reports and evaluations produced on HE institutions by EQAR registered agencies.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    local_identifier = models.CharField(max_length=255, blank=True, null=True)
    agency_esg_activity = models.ForeignKey('agencies.AgencyESGActivity', on_delete=models.PROTECT)
    name = models.CharField(max_length=300)
    status = models.ForeignKey('ReportStatus', on_delete=models.PROTECT)
    decision = models.ForeignKey('ReportDecision', on_delete=models.PROTECT)
    valid_from = models.DateField(default=datetime.date.today)
    valid_to = models.DateField(blank=True, null=True)
    institutions = models.ManyToManyField('institutions.Institution', related_name='reports')
    flag = models.ForeignKey('lists.Flag', default=1, on_delete=models.PROTECT)
    flag_log = models.TextField(blank=True)

    # Audit log values
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='reports_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(User, related_name='reports_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'deqar_reports'
        indexes = [
            models.Index(fields=['valid_from']),
            models.Index(fields=['valid_to']),
        ]
        unique_together = ('agency', 'local_identifier')


class ReportStatus(models.Model):
    """
    Status of the reports.
    """
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.status

    class Meta:
        db_table = 'deqar_report_statuses'


class ReportDecision(models.Model):
    """
    Decision described in the report.
    """
    id = models.AutoField(primary_key=True)
    decision = models.CharField(max_length=50)

    def __str__(self):
        return self.decision

    class Meta:
        db_table = 'deqar_report_decision'


class ReportLink(models.Model):
    """
    Links to records on individual reports and evaluations at agency’s site.
    """
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    link_display_name = models.CharField(max_length=200, blank=True, null=True)
    link = models.URLField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'deqar_report_links'


def set_directory_path(instance, filename):
    return '{0}/%Y%m%d-{1}'.format(instance.report.agency.acronym_primary, filename)


class ReportFile(models.Model):
    """
    PDF versions of reports and evaluations.
    """
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    file_display_name = models.CharField(max_length=255, blank=True)
    file_original_location = models.CharField(max_length=500, blank=True)
    file = models.FileField(max_length=255, blank=True, upload_to=set_directory_path)
    languages = models.ManyToManyField('lists.Language')

    class Meta:
        db_table = 'deqar_report_files'
        ordering = ['id', 'report']


class ReportFlag(models.Model):
    """
    Flags belonging to a report
    """
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    flag = models.ForeignKey('lists.Flag', on_delete=models.PROTECT)
    flag_message = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    removed_by_eqar = models.BooleanField(default=False)

    # Audit log values
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deqar_report_flags'
        ordering = ['id', 'flag__id']
        unique_together = ['report', 'flag_message']
