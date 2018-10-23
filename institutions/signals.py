from django.db.models.signals import post_save
from django.dispatch import receiver

from institutions.models import InstitutionName


@receiver(post_save, sender=InstitutionName)
def set_institution_properties(sender, instance, **kwargs):
    institution = instance.institution
    institution.set_primary_name()
    institution.set_name_sort()
    institution.save()
