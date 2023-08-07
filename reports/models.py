import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from eqar_backend.fields.char_null_field import CharNullField


class Report(models.Model):
    """
    List of reports and evaluations produced on HE institutions by EQAR registered agencies.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    contributing_agencies = models.ManyToManyField('agencies.Agency', related_name='co_authored_reports', blank=True)
    local_identifier = CharNullField(max_length=255, blank=True, null=True)
    agency_esg_activity = models.ForeignKey('agencies.AgencyESGActivity', on_delete=models.PROTECT)
    name = models.CharField(max_length=300)
    status = models.ForeignKey('ReportStatus', on_delete=models.PROTECT)
    decision = models.ForeignKey('ReportDecision', on_delete=models.PROTECT)
    summary = models.TextField(blank=True, null=True)
    valid_from = models.DateField(default=datetime.date.today)
    valid_to = models.DateField(blank=True, null=True)
    institutions = models.ManyToManyField('institutions.Institution', related_name='reports')
    flag = models.ForeignKey('lists.Flag', default=1, on_delete=models.PROTECT)
    flag_log = models.TextField(blank=True)
    other_comment = models.TextField(blank=True, null=True)
    internal_note = models.TextField(blank=True, null=True)

    # Micro credential specific fields
    mc_as_part_of_accreditation = models.BooleanField(default=False)

    # Audit log values
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='reports_created_by',
                                   on_delete=models.CASCADE, blank=True, null=True)
    updated_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(User, related_name='reports_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

    def validate_local_identifier(self):
        if self.local_identifier:
            if self.local_identifier != '':
                conflicting_instance = Report.objects.filter(
                    agency=self.agency,
                    local_identifier=self.local_identifier
                )

                if self.id:
                    # This instance has already been saved. So we need to filter out
                    # this instance from our results.
                    conflicting_instance = conflicting_instance.exclude(pk=self.id)

                if conflicting_instance.exists():
                    raise ValidationError({
                        'non_field_errors': "Report with this Agency and Local Report Identifier already exists."
                    })

    def save(self, *args, **kwargs):
        self.validate_local_identifier()
        super(Report, self).save(*args, **kwargs)

    class Meta:
        db_table = 'deqar_reports'
        verbose_name = 'Report'
        indexes = [
            models.Index(fields=['valid_from']),
            models.Index(fields=['valid_to']),
        ]


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
        verbose_name = 'Report Status'


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
        verbose_name = 'Report Decision'


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
        verbose_name = 'Report Link'


def set_directory_path(instance, filename):
    return '{0}/{1}-{2}'.format(instance.report.agency.acronym_primary,
                                datetime.datetime.now().strftime("%Y%m%d_%H%M"),
                                filename)


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
        verbose_name = 'Report File'
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
        verbose_name = 'Report Flag'
        ordering = ['id', 'flag__id']
        unique_together = ['report', 'flag_message']


class ReportUpdateLog(models.Model):
    """
    Updates happened with a report
    """
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    note = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, related_name='reports_log_updated_by',
                                   on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'deqar_report_update_log'
        verbose_name = 'Report Update Log'
