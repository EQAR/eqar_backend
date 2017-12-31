from django.db import models


class Programme(models.Model):
    """
    Institutional programmes or joint-programmes evaluated in reports.
    """
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE)
    name_primary = models.CharField(max_length=100, blank=True)
    nqf_level = models.CharField(max_length=10, blank=True)
    qf_ehea_level = models.ForeignKey('lists.QFEHEALevel', on_delete=models.SET_NULL, blank=True, null=True)
    countries = models.ManyToManyField('countries.Country')

    class Meta:
        db_table = 'deqar_programmes'


class ProgrammeName(models.Model):
    """
    One or more names of institutional programmes.
    """
    id = models.AutoField(primary_key=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    name_is_english = models.BooleanField(default=False)
    qualification = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'deqar_programme_names'
        ordering = ('name_is_english', 'name')
        unique_together = ('programme', 'name')


class ProgrammeIdentifier(models.Model):
    """
    List of identifiers for the programme and the source of the identifier.
    """
    id = models.AutoField(primary_key=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    resource = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = 'deqar_programme_identifiers'
        unique_together = ('programme', 'agency', 'resource', 'identifier')
