import sys

from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from reports.models import Report, ReportFile
from institutions.models import Institution
from reports.tasks import index_report
from submissionapi.tasks import download_file


@receiver(m2m_changed, sender=Report.institutions.through)
def set_institution_has_reports(sender, instance, action, pk_set, **kwargs):
    if pk_set:
        institutions = Institution.objects.filter(pk__in=pk_set)

        if action == 'post_add':
            for institution in institutions:
                institution.has_report = True
                institution.save()
        elif action == 'post_remove':
            for institution in institutions:
                existing = institution.reports.count()
                if existing == 0:
                    institution.has_report = False
                    institution.save()


@receiver([post_save], sender=Report)
def do_index_report(sender, instance, **kwargs):
    if 'test' not in sys.argv:
        index_report(instance.id)


@receiver([pre_save], sender=ReportFile)
def do_reharvest_file_when_location_change(sender, instance, **kwargs):
    if instance.id is not None:
        original = ReportFile.objects.get(pk=instance.pk)
        if original.file_original_location != instance.file_original_location:
            if 'test' not in sys.argv:
                download_file.delay(instance.file_original_location,
                                    instance.pk,
                                    instance.report.agency.acronym_primary)