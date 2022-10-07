import sys

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from agencies.models import Agency, AgencyESGActivity, AgencyNameVersion
from agencies.tasks import index_agency
from reports.tasks import index_report


@receiver(post_save, sender=Agency)
def do_index_agencies(sender, instance, **kwargs):
    index_agency.delay(instance.id)


@receiver(pre_save, sender=AgencyESGActivity)
def do_index_reports_upon_activity_name_change(sender, instance, **kwargs):
    if 'test' not in sys.argv:
        if instance.id is not None:
            original = AgencyESGActivity.objects.get(id=instance.id)
            if original.activity_display != instance.activity_display or \
               original.activity != instance.activity or \
               original.activity_type != instance.activity:
                for report in instance.report_set.iterator():
                    index_report.delay(report.id)
