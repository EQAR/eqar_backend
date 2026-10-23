from django.db import models


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    iso_639_1 = models.CharField(max_length=10)
    iso_639_2 = models.CharField(max_length=10, blank=True)
    language_name_en = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.language_name_en

    class Meta:
        db_table = 'deqar_list_languages'
        verbose_name = 'Language'
        ordering = ('language_name_en',)


class QFEHEALevel(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.IntegerField(blank=True, null=True)
    level = models.CharField(max_length=20)

    def __str__(self):
        return self.level

    class Meta:
        db_table = 'deqar_list_qf_ehea_levels'
        ordering = ('code',)
        verbose_name = 'QF-EHEA level'
        verbose_name_plural = 'QF-EHEA levels'


class Association(models.Model):
    id = models.AutoField(primary_key=True)
    association = models.CharField(max_length=200)

    def __str__(self):
        return self.association

    class Meta:
        db_table = 'deqar_list_associations'
        verbose_name = 'Association'
        ordering = ('association',)


class EQARDecisionType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'deqar_list_eqar_decision_types'
        verbose_name = 'EQAR Decision Type'
        verbose_name_plural = 'EQAR Decision Types'
        ordering = ('type',)


class IdentifierResource(models.Model):
    resource = models.CharField(max_length=150, primary_key=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.resource

    class Meta:
        db_table = 'deqar_list_identifier_resources'
        verbose_name = 'Identifier Resource'
        verbose_name_plural = 'Identifier Resources'
        ordering = ('resource',)


class PermissionType(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'deqar_list_permission_types'
        verbose_name = 'Permission Type'
        verbose_name_plural = 'Permission Types'
        ordering = ('type',)


class Flag(models.Model):
    id = models.AutoField(primary_key=True)
    flag = models.CharField(max_length=20)

    def __str__(self):
        return self.flag

    class Meta:
        db_table = 'deqar_list_flags'
        verbose_name = 'Flag'
        verbose_name_plural = 'Flags'
        ordering = ('id', 'flag')


class DegreeOutcome(models.Model):
    id = models.AutoField(primary_key=True)
    outcome = models.CharField(max_length=80)

    def __str__(self):
        return self.outcome

    class Meta:
        db_table = 'deqar_list_degree_outcomes'
        verbose_name = 'Degree Outcome'
        verbose_name_plural = 'Degree Outcomes'
        ordering = ('outcome',)


class Assessment(models.Model):
    id = models.AutoField(primary_key=True)
    assessment = models.CharField(max_length=50)

    def __str__(self):
        return self.assessment

    class Meta:
        db_table = 'deqar_list_assessments'
        verbose_name = 'Assessment and Certification'
        verbose_name_plural = 'Assessment and Certifications'
        ordering = ('assessment',)


class ControlledList(models.Model):
    """
    Generic controlled list with optional URI (e.g. RDF/LOD concept) and description.
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    uri = models.URLField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        ordering = ('id',)


class CrossBorderPossibility(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_cross_border_possibilities'
        verbose_name = 'Cross-border QA Possibility'
        verbose_name_plural = 'Cross-border QA Possibilities'


class CrossBorderApproval(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_cross_border_approvals'
        verbose_name = 'Cross-border QA Approval'
        verbose_name_plural = 'Cross-border QA Approvals'


class CrossBorderRequirement(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_cross_border_requirements'
        verbose_name = 'Cross-border QA Requirement'
        verbose_name_plural = 'Cross-border QA Requirements'


class CrossBorderCriteria(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_cross_border_criteria'
        verbose_name = 'Cross-border QA Criteria'
        verbose_name_plural = 'Cross-border QA Criteria'


class CrossBorderDecision(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_cross_border_decisions'
        verbose_name = 'Cross-border QA Decision'
        verbose_name_plural = 'Cross-border QA Decisions'


class EuropeanApproachPossibility(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_european_approach_possibilities'
        verbose_name = 'European Approach Possibility'
        verbose_name_plural = 'European Approach Possibilities'


class TnePossible(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_tne_possible'
        verbose_name = 'TNE Possibility'
        verbose_name_plural = 'TNE Possibilities'


class TneApprovalOutgoing(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_tne_approvals_outgoing'
        verbose_name = 'TNE Approval (outgoing)'
        verbose_name_plural = 'TNE Approvals (outgoing)'


class TneQaOutgoing(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_tne_qa_outgoing'
        verbose_name = 'TNE QA Regime (outgoing)'
        verbose_name_plural = 'TNE QA Regimes (outgoing)'


class TneOriginGroup(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_tne_origin_groups'
        verbose_name = 'TNE Origin Country Group'
        verbose_name_plural = 'TNE Origin Country Groups'


class TneApprovalIncoming(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_tne_approvals_incoming'
        verbose_name = 'TNE Approval (incoming)'
        verbose_name_plural = 'TNE Approvals (incoming)'


class TneQaIncoming(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_tne_qa_incoming'
        verbose_name = 'TNE QA Regime (incoming)'
        verbose_name_plural = 'TNE QA Regimes (incoming)'


class McQa(ControlledList):
    class Meta(ControlledList.Meta):
        db_table = 'deqar_list_mc_qa'
        verbose_name = 'Micro-credential QA Regime'
        verbose_name_plural = 'Micro-credential QA Regimes'
