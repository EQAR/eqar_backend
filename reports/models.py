from django.db import models


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    agency_identifier = models.CharField(max_length=50, blank=True, null=True)
    agency_esg_activity = models.ForeignKey('agencies.AgencyESGActivity', on_delete=models.PROTECT)
    report_name = models.CharField(max_length=300)
    report_type = models.CharField(max_length=50)
    status = models.ForeignKey('ReportStatus', on_delete=models.PROTECT)
    decision = models.ForeignKey('ReportDecision', on_delete=models.PROTECT)
    valid_from = models.DateField()
    valid_to = models.DateField(blank=True)
    institutions = models.ManyToManyField('institutions.Institution')

    class Meta:
        db_table = 'eqar_reports'


class ReportStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50)

    class Meta:
        db_table = 'eqar_report_statuses'


class ReportDecision(models.Model):
    id = models.AutoField(primary_key=True)
    decision = models.CharField(max_length=50)

    class Meta:
        db_table = 'eqar_report_decision'


class ReportFile:
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('Report')
    file_name = models.CharField(max_length=100)
    file = models.FileField()
    languages = models.ManyToManyField('lists.Language')

    class Meta:
        db_table = 'eqar_report_files'

