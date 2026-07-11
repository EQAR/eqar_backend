import datetime

from django.test import TestCase

from agencies.models import Agency
from institutions.models import (
    Institution,
    InstitutionHierarchicalRelationship,
    InstitutionHierarchicalRelationshipType,
    InstitutionHistoricalRelationship,
    InstitutionHistoricalRelationshipType,
)
from reports.models import Report, ReportStatus, ReportDecision


FIXTURES = [
    'country_qa_requirement_type', 'country', 'flag', 'permission_type',
    'qf_ehea_level', 'institution_historical_field',
    'agency_activity_type', 'agency_focus', 'identifier_resource',
    'agency_historical_field', 'eqar_decision_type',
    'agency_demo_01', 'agency_demo_02', 'association', 'submitting_agency_demo',
    'institution_relationship_type', 'institution_hierarchical_relationship_type',
    'report_status', 'report_decision',
]

# Relationship type pks from the fixtures above
TYPE_FACULTY = 2               # hierarchical, non-platform
TYPE_EDUCATIONAL_PLATFORM = 6  # hierarchical, platform (excluded)
TYPE_ALLIANCE = 7              # hierarchical, European Universities alliance (reversed report flow)
TYPE_SUCCEEDED = 2             # historical: type_from='succeeded' / type_to='succeeded by'
TYPE_ABSORBED = 3              # historical: type_from='was absorbed by' / type_to='absorbed'


class HasReportTestBase(TestCase):
    fixtures = FIXTURES

    def setUp(self):
        self.agency = Agency.objects.first()
        self.status = ReportStatus.objects.get(pk=1)
        self.decision = ReportDecision.objects.get(pk=1)

    def make_institution(self, name='Test Institution'):
        return Institution.objects.create(name_primary=name, website_link='http://example.com')

    def make_report(self, institutions=None, platforms=None,
                    valid_from=datetime.date(2015, 1, 1), valid_to=datetime.date(2030, 1, 1)):
        report = Report.objects.create(
            agency=self.agency, status=self.status, decision=self.decision,
            valid_from=valid_from, valid_to=valid_to,
        )
        if institutions:
            report.institutions.set(institutions)
        if platforms:
            report.platforms.set(platforms)
        return report

    def make_hierarchical(self, parent, child, type_id=TYPE_FACULTY, valid_from=None, valid_to=None):
        return InstitutionHierarchicalRelationship.objects.create(
            institution_parent=parent, institution_child=child,
            relationship_type=InstitutionHierarchicalRelationshipType.objects.get(pk=type_id),
            valid_from=valid_from, valid_to=valid_to,
        )

    def make_historical(self, source, target, type_id, relationship_date):
        return InstitutionHistoricalRelationship.objects.create(
            institution_source=source, institution_target=target,
            relationship_type=InstitutionHistoricalRelationshipType.objects.get(pk=type_id),
            relationship_date=relationship_date,
        )

    def make_succeeded(self, successor, predecessor, relationship_date):
        # data convention (matches webapi/v2 display serializer + PHP frontend): the successor is the
        # TARGET and the predecessor the SOURCE of a 'succeeded' (type_from='succeeded') row
        return self.make_historical(predecessor, successor, TYPE_SUCCEEDED, relationship_date)

    def make_absorbed(self, absorber, absorbed, relationship_date):
        # data convention: the absorber is the SOURCE and the absorbed institution the TARGET of an
        # 'absorbed' (type_to='absorbed') row
        return self.make_historical(absorber, absorbed, TYPE_ABSORBED, relationship_date)


class HasReportCalculationTest(HasReportTestBase):
    """calculate_has_report() across all contributor paths, honouring validity dates."""

    def test_no_report_is_false(self):
        inst = self.make_institution()
        self.assertFalse(inst.calculate_has_report())

    def test_direct_report_is_true(self):
        inst = self.make_institution()
        self.make_report(institutions=[inst])
        self.assertTrue(inst.calculate_has_report())

    def test_platform_report_is_true(self):
        inst = self.make_institution()
        self.make_report(platforms=[inst])
        self.assertTrue(inst.calculate_has_report())

    def test_child_faculty_report_marks_parent(self):
        parent = self.make_institution('Parent')
        child = self.make_institution('Faculty')
        self.make_hierarchical(parent, child, TYPE_FACULTY)
        self.make_report(institutions=[child])
        self.assertTrue(parent.calculate_has_report())
        # child obviously has its own report too
        self.assertTrue(child.calculate_has_report())

    def test_educational_platform_child_does_not_mark_parent(self):
        parent = self.make_institution('Platform')
        child = self.make_institution('Hosted institution')
        self.make_hierarchical(parent, child, TYPE_EDUCATIONAL_PLATFORM)
        self.make_report(institutions=[child])
        self.assertFalse(parent.calculate_has_report())

    def test_child_report_outside_valid_window_excluded(self):
        parent = self.make_institution('Parent')
        child = self.make_institution('Faculty')
        # relationship only valid until 2012, but the child report starts in 2015
        self.make_hierarchical(parent, child, TYPE_FACULTY,
                               valid_from=datetime.date(2010, 1, 1), valid_to=datetime.date(2012, 1, 1))
        self.make_report(institutions=[child],
                         valid_from=datetime.date(2015, 1, 1), valid_to=datetime.date(2016, 1, 1))
        self.assertFalse(parent.calculate_has_report())

    def test_child_report_inside_valid_window_included(self):
        parent = self.make_institution('Parent')
        child = self.make_institution('Faculty')
        self.make_hierarchical(parent, child, TYPE_FACULTY,
                               valid_from=datetime.date(2010, 1, 1), valid_to=datetime.date(2020, 1, 1))
        self.make_report(institutions=[child],
                         valid_from=datetime.date(2015, 1, 1), valid_to=datetime.date(2016, 1, 1))
        self.assertTrue(parent.calculate_has_report())

    def test_historical_succeeded_within_window(self):
        successor = self.make_institution('Successor')
        predecessor = self.make_institution('Predecessor')
        # successor succeeded predecessor in 2014; predecessor report valid until 2030
        self.make_succeeded(successor, predecessor, datetime.date(2014, 1, 1))
        self.make_report(institutions=[predecessor],
                         valid_from=datetime.date(2015, 1, 1), valid_to=datetime.date(2030, 1, 1))
        self.assertTrue(successor.calculate_has_report())

    def test_historical_succeeded_outside_window(self):
        successor = self.make_institution('Successor')
        predecessor = self.make_institution('Predecessor')
        # successor succeeded predecessor in 2014; predecessor report expired in 2012
        self.make_succeeded(successor, predecessor, datetime.date(2014, 1, 1))
        self.make_report(institutions=[predecessor],
                         valid_from=datetime.date(2008, 1, 1), valid_to=datetime.date(2012, 1, 1))
        self.assertFalse(successor.calculate_has_report())

    def test_historical_absorbed(self):
        absorber = self.make_institution('Absorber')
        absorbed = self.make_institution('Absorbed')
        # absorber absorbed 'absorbed' in 2014
        self.make_absorbed(absorber, absorbed, datetime.date(2014, 1, 1))
        self.make_report(institutions=[absorbed],
                         valid_from=datetime.date(2015, 1, 1), valid_to=datetime.date(2030, 1, 1))
        self.assertTrue(absorber.calculate_has_report())

    def test_valid_to_calculated_branch_without_valid_to(self):
        # report with no valid_to -> valid_to_calculated = valid_from + 6 years
        successor = self.make_institution('Successor')
        predecessor = self.make_institution('Predecessor')
        # relationship in 2014; report valid_from 2010, no valid_to -> effective end 2016 (>= 2014) -> included
        self.make_succeeded(successor, predecessor, datetime.date(2014, 1, 1))
        self.make_report(institutions=[predecessor],
                         valid_from=datetime.date(2010, 1, 1), valid_to=None)
        self.assertTrue(successor.calculate_has_report())

    def test_valid_to_calculated_branch_expires_before_window(self):
        successor = self.make_institution('Successor')
        predecessor = self.make_institution('Predecessor')
        # relationship in 2020; report valid_from 2010, no valid_to -> effective end 2016 (< 2020) -> excluded
        self.make_succeeded(successor, predecessor, datetime.date(2020, 1, 1))
        self.make_report(institutions=[predecessor],
                         valid_from=datetime.date(2010, 1, 1), valid_to=None)
        self.assertFalse(successor.calculate_has_report())

    # --- regression: direction of historical report inheritance (must match the webapi/v2 detail
    # serializer + PHP frontend). These pin the raw on-disk source/target orientation so the
    # traversal cannot silently re-invert. ---

    def test_successor_inherits_predecessor_not_the_reverse(self):
        # "A succeeded B in 2024": stored as source=B (predecessor), target=A (successor) on a
        # type_from='succeeded' row -- exactly what the detail serializer flattens to
        # relationship_type='succeeded' on A's side.
        successor = self.make_institution('A (successor)')
        predecessor = self.make_institution('B (predecessor)')
        self.make_historical(predecessor, successor, TYPE_SUCCEEDED, datetime.date(2024, 1, 1))
        # B's report is still valid past the succession date
        self.make_report(institutions=[predecessor],
                         valid_from=datetime.date(2022, 1, 1), valid_to=datetime.date(2026, 1, 1))
        # A (successor) inherits B's report; B does not inherit anything from A
        self.assertIn(predecessor.id, [c[0] for c in successor.get_report_contributors()])
        self.assertNotIn(successor.id, [c[0] for c in predecessor.get_report_contributors()])
        self.assertTrue(successor.calculate_has_report())

    def test_predecessor_does_not_inherit_successor_reports(self):
        successor = self.make_institution('A (successor)')
        predecessor = self.make_institution('B (predecessor)')
        self.make_historical(predecessor, successor, TYPE_SUCCEEDED, datetime.date(2024, 1, 1))
        # only the successor has a report -> the predecessor must NOT be credited with it
        self.make_report(institutions=[successor],
                         valid_from=datetime.date(2022, 1, 1), valid_to=datetime.date(2026, 1, 1))
        self.assertFalse(predecessor.calculate_has_report())

    def test_absorber_inherits_absorbed_not_the_reverse(self):
        # "A absorbed B in 2024": stored as source=A (absorber), target=B (absorbed) on a
        # type_to='absorbed' row.
        absorber = self.make_institution('A (absorber)')
        absorbed = self.make_institution('B (absorbed)')
        self.make_historical(absorber, absorbed, TYPE_ABSORBED, datetime.date(2024, 1, 1))
        self.make_report(institutions=[absorbed],
                         valid_from=datetime.date(2022, 1, 1), valid_to=datetime.date(2026, 1, 1))
        self.assertIn(absorbed.id, [c[0] for c in absorber.get_report_contributors()])
        self.assertNotIn(absorber.id, [c[0] for c in absorbed.get_report_contributors()])
        self.assertTrue(absorber.calculate_has_report())

    # --- European Universities alliance (type 7): report flow is reversed vs. ordinary hierarchy.
    # The alliance is the PARENT and its member HEIs the CHILDREN, but the alliance's reports show
    # on the members, not the other way round. ---

    def test_alliance_report_marks_member_hei(self):
        alliance = self.make_institution('Alliance')
        member = self.make_institution('Member HEI')
        self.make_hierarchical(alliance, member, TYPE_ALLIANCE)
        self.make_report(institutions=[alliance])
        # member (child) inherits the alliance's (parent's) report
        self.assertIn(alliance.id, [c[0] for c in member.get_report_contributors()])
        self.assertTrue(member.calculate_has_report())

    def test_alliance_does_not_inherit_member_reports(self):
        alliance = self.make_institution('Alliance')
        member = self.make_institution('Member HEI')
        self.make_hierarchical(alliance, member, TYPE_ALLIANCE)
        self.make_report(institutions=[member])
        # the alliance (parent) must NOT be credited with a member's report
        self.assertNotIn(member.id, [c[0] for c in alliance.get_report_contributors()])
        self.assertFalse(alliance.calculate_has_report())

    def test_alliance_report_honours_validity_window(self):
        alliance = self.make_institution('Alliance')
        member = self.make_institution('Member HEI')
        # membership only valid until 2012, but the alliance report starts in 2015
        self.make_hierarchical(alliance, member, TYPE_ALLIANCE,
                               valid_from=datetime.date(2010, 1, 1), valid_to=datetime.date(2012, 1, 1))
        self.make_report(institutions=[alliance],
                         valid_from=datetime.date(2015, 1, 1), valid_to=datetime.date(2016, 1, 1))
        self.assertFalse(member.calculate_has_report())


class ReportViewsFilterParityTest(HasReportTestBase):
    """
    The report_views Meili filters are built from the same get_report_contributors() enumeration.
    This locks in the exact filter strings (parity with the previous inline implementation).
    """

    def ts(self, d):
        return int(datetime.datetime.combine(d, datetime.datetime.min.time()).timestamp())

    def build_scenario(self):
        inst = self.make_institution('Main')
        faculty = self.make_institution('Faculty')
        hosted = self.make_institution('Hosted on platform')
        predecessor = self.make_institution('Predecessor')
        absorbed = self.make_institution('Absorbed')

        self.vf, self.vt = datetime.date(2010, 1, 1), datetime.date(2020, 1, 1)
        self.make_hierarchical(inst, faculty, TYPE_FACULTY, valid_from=self.vf, valid_to=self.vt)
        self.make_hierarchical(inst, hosted, TYPE_EDUCATIONAL_PLATFORM)  # excluded
        self.succeeded_date = datetime.date(2014, 1, 1)
        self.make_succeeded(inst, predecessor, self.succeeded_date)
        self.absorbed_date = datetime.date(2016, 1, 1)
        self.make_absorbed(inst, absorbed, self.absorbed_date)

        self.inst, self.faculty, self.predecessor, self.absorbed = inst, faculty, predecessor, absorbed
        return inst

    def test_reports_index_filters(self):
        from webapi.v2.views.report_views import institution_report_meili_filters
        inst = self.build_scenario()
        expected = [
            f'institutions.id = {inst.id}',
            f'platforms.id = {inst.id}',
            f'( institutions.id = {self.faculty.id} OR platforms.id = {self.faculty.id} )'
            f' AND valid_to_calculated >= {self.ts(self.vf)}'
            f' AND valid_from <= {self.ts(self.vt)}',
            f'institutions.id = {self.predecessor.id} AND valid_to_calculated >= {self.ts(self.succeeded_date)}',
            f'institutions.id = {self.absorbed.id} AND valid_to_calculated >= {self.ts(self.absorbed_date)}',
        ]
        self.assertEqual(institution_report_meili_filters(inst, 'INDEX_REPORTS'), expected)

    def test_programmes_index_filters(self):
        from webapi.v2.views.report_views import institution_report_meili_filters
        inst = self.build_scenario()
        expected = [
            f'institutions = {inst.id}',
            f'platforms = {inst.id}',
            f'( institutions = {self.faculty.id} OR platforms = {self.faculty.id} )'
            f' AND report.valid_to_calculated >= {self.ts(self.vf)}'
            f' AND report.valid_from <= {self.ts(self.vt)}',
            f'institutions = {self.predecessor.id} AND report.valid_to_calculated >= {self.ts(self.succeeded_date)}',
            f'institutions = {self.absorbed.id} AND report.valid_to_calculated >= {self.ts(self.absorbed_date)}',
        ]
        self.assertEqual(institution_report_meili_filters(inst, 'INDEX_PROGRAMMES'), expected)


class HasReportSignalTest(HasReportTestBase):
    """Signals keep the persisted has_report flag in sync with report and relationship changes."""

    def refresh(self, inst):
        return Institution.objects.get(pk=inst.pk)

    def test_direct_report_add_and_remove(self):
        inst = self.make_institution()
        report = self.make_report(institutions=[inst])
        self.assertTrue(self.refresh(inst).has_report)
        report.institutions.remove(inst)
        self.assertFalse(self.refresh(inst).has_report)

    def test_add_report_to_child_flips_parent(self):
        parent = self.make_institution('Parent')
        child = self.make_institution('Faculty')
        self.make_hierarchical(parent, child, TYPE_FACULTY)
        self.assertFalse(self.refresh(parent).has_report)
        self.make_report(institutions=[child])
        self.assertTrue(self.refresh(parent).has_report)

    def test_remove_report_from_child_flips_parent_back(self):
        parent = self.make_institution('Parent')
        child = self.make_institution('Faculty')
        self.make_hierarchical(parent, child, TYPE_FACULTY)
        report = self.make_report(institutions=[child])
        self.assertTrue(self.refresh(parent).has_report)
        report.institutions.remove(child)
        self.assertFalse(self.refresh(parent).has_report)

    def test_platform_report_sets_flag(self):
        inst = self.make_institution()
        self.make_report(platforms=[inst])
        self.assertTrue(self.refresh(inst).has_report)

    def test_creating_hierarchical_relationship_recomputes_parent(self):
        parent = self.make_institution('Parent')
        child = self.make_institution('Faculty')
        self.make_report(institutions=[child])
        self.assertFalse(self.refresh(parent).has_report)
        # linking the child to the parent should now flip the parent's flag
        self.make_hierarchical(parent, child, TYPE_FACULTY)
        self.assertTrue(self.refresh(parent).has_report)

    def test_deleting_hierarchical_relationship_recomputes_parent(self):
        parent = self.make_institution('Parent')
        child = self.make_institution('Faculty')
        self.make_report(institutions=[child])
        rel = self.make_hierarchical(parent, child, TYPE_FACULTY)
        self.assertTrue(self.refresh(parent).has_report)
        rel.delete()
        self.assertFalse(self.refresh(parent).has_report)

    def test_creating_historical_relationship_recomputes(self):
        successor = self.make_institution('Successor')
        predecessor = self.make_institution('Predecessor')
        self.make_report(institutions=[predecessor],
                         valid_from=datetime.date(2015, 1, 1), valid_to=datetime.date(2030, 1, 1))
        self.assertFalse(self.refresh(successor).has_report)
        self.make_succeeded(successor, predecessor, datetime.date(2014, 1, 1))
        self.assertTrue(self.refresh(successor).has_report)

    def test_alliance_report_flips_member_flag(self):
        alliance = self.make_institution('Alliance')
        member = self.make_institution('Member HEI')
        self.make_hierarchical(alliance, member, TYPE_ALLIANCE)
        self.assertFalse(self.refresh(member).has_report)
        # adding a report to the alliance (parent) must recompute the member (child) via dependents
        report = self.make_report(institutions=[alliance])
        self.assertTrue(self.refresh(member).has_report)
        # the alliance itself is credited with its own report; the member's report is not required
        report.institutions.remove(alliance)
        self.assertFalse(self.refresh(member).has_report)

    def test_member_report_does_not_flip_alliance_flag(self):
        alliance = self.make_institution('Alliance')
        member = self.make_institution('Member HEI')
        self.make_hierarchical(alliance, member, TYPE_ALLIANCE)
        self.make_report(institutions=[member])
        self.assertFalse(self.refresh(alliance).has_report)
