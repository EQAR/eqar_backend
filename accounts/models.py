from django.contrib.auth.models import User
from django.db import models


class DEQARProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    submitting_agency = models.ForeignKey('agencies.SubmittingAgency', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = [ 'user__username' ]

