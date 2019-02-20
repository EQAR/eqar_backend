from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from reports.models import Report
from institutions.models import Institution
from reports.tasks import index_report


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
    index_report.delay(instance.id)
