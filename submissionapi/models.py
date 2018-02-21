import datetime
from django.db import models


# Create your models here.
class SubmissionLog(models.Model):
    id = models.AutoField(primary_key=True)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE)
    submitted_data = models.TextField(blank=True)
    report_status = models.CharField(max_length=20, default='success')
    report_warnings = models.TextField(blank=True)
    institution_warnings = models.TextField(blank=True)
    country_warnings = models.TextField(blank=True)
    submission_date = models.DateField(default=datetime.date.today)

    class Meta:
        db_table = 'deqar_submission_log'
