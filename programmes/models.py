from django.db import models

NQF_LEVEL_CHOICES = (('level 6', 'level 6'), ('level 7', 'level 7'), ('level 8', 'level 8'))


class Programme(models.Model):
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE)
    qualification = models.CharField(max_length=100, blank=True)
    nqf_level = models.CharField(max_length=10, choices=NQF_LEVEL_CHOICES)
    qf_ehea_level = models.ForeignKey('lists.QFEHEALevel', on_delete=models.PROTECT)
    countries = models.ManyToManyField('lists.Country')

    class Meta:
        db_table = 'eqar_programmes'


class ProgrammeNames(models.Model):
    id = models.AutoField(primary_key=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    name_is_english = models.BooleanField(default=False)

    class Meta:
        db_table = 'eqar_programme_names'
