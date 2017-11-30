from django.db import models


class Programme(models.Model):
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE)
    nqf_level = models.CharField(max_length=10, blank=True)
    qf_ehea_level = models.ForeignKey('lists.QFEHEALevel', on_delete=models.SET_NULL, blank=True, null=True)
    countries = models.ManyToManyField('lists.Country')

    class Meta:
        db_table = 'eqar_programmes'


class ProgrammeNames(models.Model):
    id = models.AutoField(primary_key=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    name_is_english = models.BooleanField(default=False)
    qualification = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'eqar_programme_names'
