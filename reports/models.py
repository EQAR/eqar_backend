from django.db import models


class Report(models.Model):
    """
    List of reports and evaluations produced on HE institutions by EQAR registered agencies.
    """
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    local_identifier = models.CharField(max_length=50, blank=True, null=True)
    agency_esg_activity = models.ForeignKey('agencies.AgencyESGActivity', on_delete=models.PROTECT)
    name = models.CharField(max_length=300)
    status = models.ForeignKey('ReportStatus', on_delete=models.PROTECT)
    decision = models.ForeignKey('ReportDecision', on_delete=models.PROTECT)
    valid_from = models.DateField()
    valid_to = models.DateField(blank=True)
    institutions = models.ManyToManyField('institutions.Institution', related_name='reports')

    class Meta:
        db_table = 'deqar_reports'


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


class ReportFile:
    """
    PDF versions of reports and evaluations.
    """
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('Report')
    file_display_name = models.CharField(max_length=100)
    file = models.FileField()
    languages = models.ManyToManyField('lists.Language')

    class Meta:
        db_table = 'deqar_report_files'

