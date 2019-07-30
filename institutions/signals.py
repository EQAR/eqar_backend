from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from institutions.models import InstitutionName, Institution
from institutions.tasks import index_institution


@receiver([post_save, post_delete], sender=Institution)
def do_index_institutions_upon_institution_save(sender, instance, **kwargs):
    index_institution.delay(instance.id)


@receiver([post_save, post_delete], sender=InstitutionName)
def set_institution_properties(sender, instance, **kwargs):
    institution = instance.institution
    institution.set_primary_name()
    institution.set_name_sort()
    institution.save()
