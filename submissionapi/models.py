import datetime
from django.db import models


class SubmissionPackageLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('accounts.DEQARProfile', on_delete=models.CASCADE)
    user_ip_address = models.GenericIPAddressField(blank=True, null=True)
    origin = models.CharField(max_length=10, blank=True, null=True)
    submitted_data = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} from {self.user_ip_address} via {self.origin} @ {self.submission_date}"

    class Meta:
        db_table = 'deqar_submission_package_log'


class SubmissionReportLog(models.Model):
    id = models.AutoField(primary_key=True)
    submission_package_log = models.ForeignKey('SubmissionPackageLog', on_delete=models.CASCADE)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE)
    report_status = models.CharField(max_length=20, default='success')
    report_warnings = models.TextField(blank=True)
    institution_warnings = models.TextField(blank=True)
    country_warnings = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deqar_submission_report_log'

