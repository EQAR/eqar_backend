import time

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from agencies.models import Agency, AgencyESGActivity
from agencies.tasks import index_agency, index_institutions_when_agency_saved
from reports.tasks import index_report


@receiver([post_save, post_delete], sender=Agency)
def do_index_institutions_upon_agency_save(sender, instance, **kwargs):
    index_institutions_when_agency_saved.delay(instance.id)


@receiver([post_save], sender=Agency)
def do_index_agencies(sender, instance, **kwargs):
    index_agency.delay(instance.id)


@receiver([post_save], sender=AgencyESGActivity)
def do_index_reports_upon_activity_name_change(sender, instance, **kwargs):
    for report in instance.report_set.iterator():
        index_report.delay(report.id)

