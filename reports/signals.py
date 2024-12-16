import sys

from django.db import transaction
from django.db.models.signals import m2m_changed, post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver

from reports.models import Report, ReportFile
from institutions.models import Institution
from reports.tasks import index_report, meili_index_report, index_delete_report, meili_delete_report
from institutions.tasks import index_institution
from submissionapi.tasks import download_file


@receiver(m2m_changed, sender=Report.institutions.through)
def set_institution_has_reports(sender, instance, action, pk_set, **kwargs):
    if pk_set:
        institutions = Institution.objects.filter(pk__in=pk_set)

        if action == 'post_add':
            institutions.update(has_report=True)
            # deliberately avoids post_save signals and indexation, since institutions will be indexed anyhow on report save
        elif action == 'post_remove':
            for institution in institutions:
                existing = institution.reports.count()
                if institution.has_report and existing == 0:
                    institution.has_report = False
                    institution.save()


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
                download_file.delay(instance.file_original_location,
                                    instance.pk,
                                    instance.report.agency.acronym_primary)
