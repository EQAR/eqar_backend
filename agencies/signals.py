import sys
from functools import partial

from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from agencies.models import (
    Agency,
    AgencyActivityGroup,
    AgencyActivityType,
    AgencyESGActivity,
    AgencyNameVersion,
)
from agencies.tasks import index_agency
from reports.models import Report
from reports.tasks import index_report, meili_index_report


def _schedule_report_reindex(report_ids):
    for report_id in report_ids:
        transaction.on_commit(partial(index_report.delay, report_id))
        transaction.on_commit(partial(meili_index_report.delay, report_id))


def _mark_reports_for_reindex(instance, report_ids):
    instance._search_report_ids_to_reindex = list(report_ids)


@receiver(post_save, sender=AgencyESGActivity)
@receiver(post_save, sender=AgencyActivityGroup)
@receiver(post_save, sender=AgencyActivityType)
def do_index_reports_upon_activity_change(sender, instance, **kwargs):
    report_ids = instance.__dict__.pop('_search_report_ids_to_reindex', None)
    if 'test' not in sys.argv and report_ids is not None:
        _schedule_report_reindex(report_ids)


@receiver(post_save, sender=Agency)
def do_index_agencies(sender, instance, **kwargs):
    index_agency.delay(instance.id)


@receiver(pre_save, sender=AgencyESGActivity)
def mark_reports_upon_activity_change(sender, instance, **kwargs):
    if 'test' not in sys.argv:
        if instance.id is not None:
            original = AgencyESGActivity.objects.get(id=instance.id)
            if original.activity_display != instance.activity_display or \
               original.activity != instance.activity or \
               original.activity_group_id != instance.activity_group_id:
                report_ids = instance.reports.values_list('id', flat=True)
                _mark_reports_for_reindex(instance, report_ids)


@receiver(pre_save, sender=AgencyActivityGroup)
def mark_reports_upon_activity_group_type_change(sender, instance, **kwargs):
    if 'test' not in sys.argv and instance.id is not None:
        original = AgencyActivityGroup.objects.get(id=instance.id)
        if original.activity_type_id != instance.activity_type_id:
            report_ids = Report.objects.filter(
                agency_esg_activities__activity_group_id=instance.id
            ).values_list('id', flat=True).distinct()
            _mark_reports_for_reindex(instance, report_ids)


@receiver(pre_save, sender=AgencyActivityType)
def mark_reports_upon_activity_type_name_change(sender, instance, **kwargs):
    if 'test' not in sys.argv and instance.id is not None:
        original = AgencyActivityType.objects.get(id=instance.id)
        if original.type != instance.type:
            report_ids = Report.objects.filter(
                agency_esg_activities__activity_group__activity_type_id=instance.id
            ).values_list('id', flat=True).distinct()
            _mark_reports_for_reindex(instance, report_ids)
