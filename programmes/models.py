from django.db import models


class Programme(models.Model):
    """
    Institutional programmes or joint-programmes evaluated in reports.
    """
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey('reports.Report', on_delete=models.CASCADE)
    name_primary = models.CharField(max_length=255, blank=True)
    nqf_level = models.CharField(max_length=255, blank=True)
    qf_ehea_level = models.ForeignKey('lists.QFEHEALevel', on_delete=models.SET_NULL, blank=True, null=True)
    countries = models.ManyToManyField('countries.Country', blank=True)

    # Micro credential specific fields
    degree_outcome = models.ForeignKey('lists.DegreeOutcome', default=2, on_delete=models.PROTECT)
    ects_credit = models.ForeignKey('lists.ECTSCredit', on_delete=models.SET_NULL, blank=True, null=True)
    assessment = models.ForeignKey('lists.Assessment', on_delete=models.SET_NULL, blank=True, null=True)
    isced = models.CharField(max_length=70, blank=True, null=True)
    mc_as_part_of_accreditation = models.BooleanField(default=False)

    class Meta:
        db_table = 'deqar_programmes'
        verbose_name = 'Programmme'
        indexes = [
            models.Index(fields=['name_primary']),
        ]
        ordering = ['id', 'report']

    def __str__(self):
        return self.name_primary

    def set_primary_name(self):
        prg_name_primary = self.programmename_set.filter(name_is_primary=True).first()
        if prg_name_primary is not None:
            self.name_primary = prg_name_primary.name
            self.save()


class ProgrammeName(models.Model):
    """
    One or more names of institutional programmes.
    """
    id = models.AutoField(primary_key=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    name_is_primary = models.BooleanField(default=False)
    qualification = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'deqar_programme_names'
        verbose_name = 'Programme Name'
        ordering = ('-name_is_primary', 'name')
        unique_together = ('programme', 'name')


class ProgrammeIdentifier(models.Model):
    """
    List of identifiers for the programme and the source of the identifier.
    """
    id = models.AutoField(primary_key=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    identifier = models.CharField(max_length=50)
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    resource = models.CharField(max_length=200, blank=True, default='local identifier')

    class Meta:
        db_table = 'deqar_programme_identifiers'
        verbose_name = 'Programme Identifier'
        unique_together = ('programme', 'agency', 'resource')


class ProgrammeLearningOutcome(models.Model):
    """
    List of learning outcomes from the ESCO terminology
    """
    id = models.AutoField(primary_key=True)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    learning_outcome = models.CharField(max_length=70, blank=True, null=True)
    learning_outcome_description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'deqar_programme_learning_outcomes'
        verbose_name = 'Programme Learning Outcome'
        unique_together = ('programme', 'learning_outcome')