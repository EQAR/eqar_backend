import time

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from agencies.models import Agency, AgencyESGActivity
from agencies.tasks import index_agency
from institutions.models import Institution
from institutions.tasks import index_institution
from reports.tasks import index_report


@receiver([post_save, post_delete], sender=Agency)
def do_index_institutions_upon_agency_save(sender, instance, **kwargs):
    institutions = Institution.objects.filter(reports__agency=instance)
    for inst in institutions.all():
        index_institution.delay(inst.id)


@receiver([post_save], sender=Agency)
def do_index_agencies(sender, instance, **kwargs):
    index_agency.delay(instance.id)


@receiver([post_save], sender=AgencyESGActivity)
def do_index_reports_upon_activity_name_change(sender, instance, **kwargs):
    for report in instance.report_set.iterator():
        index_report.delay(report.id)

