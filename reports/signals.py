import sys

from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from reports.models import Report, ReportFile
from institutions.models import Institution
from reports.tasks import index_report, meili_index_report, index_delete_report, meili_delete_report
from institutions.tasks import index_institution, meili_index_institution
from submissionapi.tasks import download_file


@receiver(m2m_changed, sender=Report.institutions.through)
@receiver(m2m_changed, sender=Report.platforms.through)
def set_institution_has_reports(sender, instance, action, pk_set, **kwargs):
    """
    Keep Institution.has_report in sync when a report's institution/platform links change.

    Recomputes the flag (via the canonical Institution.calculate_has_report) not only for the
    directly affected institutions but also for their dependents - i.e. parents/predecessors that
    inherit their reports through hierarchical/historical relationships.

    Institutions whose flag changed are reindexed, except the report's own (direct) institutions,
    which meili_index_report already reindexes on report save - avoiding double reindexing.
    """
    # Only handle the forward direction (report.institutions / report.platforms), where pk_set holds
    # institution ids and `instance` is the Report. The reverse direction is not used here.
    if not isinstance(instance, Report):
        return

    # pre_clear fires while the links still exist: snapshot them so post_clear can recompute
    if action == 'pre_clear':
        instance._has_report_cleared_ids = set(
            sender.objects.filter(report_id=instance.pk).values_list('institution_id', flat=True)
        )
        return

    if action == 'post_clear':
        affected_ids = getattr(instance, '_has_report_cleared_ids', set())
    elif action in ('post_add', 'post_remove') and pk_set:
        affected_ids = set(pk_set)
    else:
        return

    # collect the affected institutions plus everyone whose flag depends on them
    recompute_ids = set()
    for institution in Institution.objects.filter(pk__in=affected_ids):
        recompute_ids |= institution.get_report_dependents()

    changed_ids = [
        institution.pk
        for institution in Institution.objects.filter(pk__in=recompute_ids)
        if institution.update_has_report()
    ]

    # meili_index_report already reindexes the report's direct institutions on save
    direct_ids = set(instance.institutions.values_list('pk', flat=True))
    reindex_ids = [pk for pk in changed_ids if pk not in direct_ids]

    if reindex_ids and 'test' not in sys.argv:
        for institution_id in reindex_ids:
            transaction.on_commit(lambda i=institution_id: index_institution.delay(i))
            transaction.on_commit(lambda i=institution_id: meili_index_institution.delay(i))


@receiver([post_save], sender=Report)
def do_index_report(sender, instance, **kwargs):
    if 'test' not in sys.argv:
        transaction.on_commit(lambda: index_report.delay(instance.id))
        transaction.on_commit(lambda: meili_index_report.delay(instance.id))


@receiver([pre_delete], sender=Report)
def do_delete_report(sender, instance, **kwargs):
    report_id = instance.id
    programme_ids = [ p.id for p in instance.programme_set.iterator() ]
    institution_ids = [ i.id for i in instance.institutions.iterator() ]
    transaction.on_commit(lambda: index_delete_report.delay(report_id))
    transaction.on_commit(lambda: meili_delete_report.delay(report_id, programme_ids, institution_ids))


@receiver([pre_save], sender=ReportFile)
def do_reharvest_file_when_location_change(sender, instance, **kwargs):
    if 'test' not in sys.argv:
        if instance.id is not None:
            original = ReportFile.objects.get(pk=instance.pk)
            if original.file_original_location != instance.file_original_location:
                if instance.file_original_location:
                    instance.download_status = ReportFile.DOWNLOAD_STATUS_PENDING
                else:
                    instance.download_status = ''
                download_file.delay(instance.file_original_location,
                                    instance.pk,
                                    instance.report.agency.acronym_primary)
