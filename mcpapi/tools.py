"""
Tools of the DEQAR MCP server. Each tool is a plain (synchronous) function returning a dict; the type hints and
docstrings are published as the tool schemas and descriptions (see mcpapi.server).
"""
import datetime

from typing import Annotated, Literal, Optional

from django.conf import settings
from django.db.models import Count, Q
from pydantic import Field

from agencies.models import Agency, AgencyActivityGroup, AgencyActivityType, AgencyFocusCountry
from countries.models import Country, CountryInstitutionType
from lists.models import Flag, Language, PermissionType, QFEHEALevel
from reports.models import Report, ReportDecision, ReportStatus
from webapi.v2.serializers.country_serializers import CountryDetailSerializer
from webapi.v2.views.country_views import CountryDetail
from webapi.v2.views.institution_views import build_institution_filters
from webapi.v2.views.report_search_views import build_report_filters
from webapi.v2.views.report_views import institution_report_meili_filters

from mcpapi import resolvers
from mcpapi.context import public_request
from mcpapi.exceptions import ToolInputError
from mcpapi.search import meili_search
from mcpapi.serializers import McpAgencyDetailSerializer, McpInstitutionDetailSerializer, McpReportDetailSerializer
from mcpapi.shaping import collapse_controlled_lists, deqar_url, paginated, timestamp_to_isodate

# lists.Flag: reports flagged 'high level' are hidden, as on the DEQAR website
FLAG_HIGH_LEVEL_ID = 3

# lists.PermissionType values used for country-level permissions
PERMISSION_TYPE_IDS = {
    'yes': 1,
    'no': 2,
    'partially / with conditions': 3,
}

# values of Programme.get_programme_type()
PROGRAMME_TYPES = ('Full recognised degree programme', 'Micro-credential', 'Other provision')

MAX_FACET_VALUES = 30
MAX_REFERENCE_VALUES = 100
MAX_LISTED_INSTITUTIONS = 5
MAX_LISTED_PROGRAMMES = 3

# argument types shared by several tools
Limit = Annotated[int, Field(ge=0, le=settings.MCP_MAX_LIMIT,
                             description='Number of results to return; 0 returns only the total (and facets)')]
Offset = Annotated[int, Field(ge=0, le=settings.MCP_MAX_OFFSET,
                              description='Number of results to skip; pass next_offset of the previous page')]
Query = Annotated[Optional[str], Field(max_length=200, description='Free-text search')]
CountryRef = Annotated[str, Field(min_length=1, max_length=100,
                                  description='Country: DEQAR ID, ISO 3166 alpha-2 or alpha-3 code, or English name')]
OptionalCountryRef = Annotated[Optional[str], Field(min_length=1, max_length=100,
                                  description='Country: DEQAR ID, ISO 3166 alpha-2 or alpha-3 code, or English name')]
OptionalAgencyRef = Annotated[Optional[str], Field(min_length=1, max_length=200,
                                  description='Agency: DEQAR ID, current or former acronym, or name')]
Permission = Literal['yes', 'no', 'partially / with conditions']
ActivityType = Literal['institutional', 'programme', 'joint programme', 'institutional/programme']
QfEheaLevel = Literal['short cycle', 'first cycle', 'second cycle', 'third cycle']


def _bool_param(value):
    """
    boolean as accepted by the Web API filter builders (BooleanExtendedField)
    """
    return None if value is None else ('true' if value else 'false')


def _facet_counts(distribution, lookup=None):
    """
    non-zero facet counts, largest first, with IDs replaced by labels via lookup (dict)
    """
    counts = sorted(((k, v) for k, v in distribution.items() if v), key=lambda i: -i[1])[:MAX_FACET_VALUES]
    if lookup is not None:
        return { lookup.get(int(k), k): v for k, v in counts }
    return dict(counts)


# --- countries ---

COUNTRY_OVERVIEW_FIELDS = [
    'ehea_is_member', 'eqar_governmental_member_start', 'external_QAA_is_permitted',
    'european_approach_is_permitted', 'ehea_key_commitment', 'qa_requirement_note', 'general_note',
    'lrc_signatory_date', 'qf_ehea_alignment_date', 'eqf_alignment_date', 'has_full_institution_list',
    'report_count', 'institution_count',
]

COUNTRY_GROUP_SECTIONS = {
    'qa_requirements': ['combination_logic', 'requirements', 'regulations'],
    'outgoing_tne': ['outgoing_tne_possible', 'outgoing_tne_conditions', 'outgoing_tne_approval', 'outgoing_tne_qa'],
    'microcredentials': ['mc_possible', 'mc_credit_limit', 'mc_qa', 'mc_qa_note'],
}

CountrySection = Literal['overview', 'qaa_regulations', 'qa_requirements', 'outgoing_tne', 'microcredentials',
                         'incoming_tne']


def list_countries(
    ehea_only: Annotated[bool, Field(description='Only countries of the European Higher Education Area (EHEA)')] = True,
    external_qaa: Annotated[Optional[Permission], Field(
        description='Only countries where institutions may (yes), may not (no) or may with conditions use a '
                    'suitable EQAR-registered agency from abroad for their external QA')] = None,
    european_approach: Annotated[Optional[Permission], Field(
        description='Only countries where the European Approach for QA of joint programmes is permitted, not '
                    'permitted or permitted with conditions')] = None,
) -> dict:
    """
    List countries with their headline QA framework indicators: whether higher education institutions may use an
    EQAR-registered agency from abroad (external_qaa_permitted), whether the European Approach for joint
    programmes is permitted, EQAR governmental membership, EHEA key commitment status, and the number of
    EQAR-registered agencies based in the country. Use get_country for the full QA framework of one country.
    """
    countries = Country.objects.annotate(agency_count=Count('agency', filter=Q(agency__is_registered=True)))
    if ehea_only:
        countries = countries.filter(ehea_is_member=True)
    if external_qaa:
        countries = countries.filter(external_QAA_is_permitted_id=PERMISSION_TYPE_IDS[external_qaa])
    if european_approach:
        countries = countries.filter(european_approach_is_permitted_id=PERMISSION_TYPE_IDS[european_approach])

    results = [
        {
            'id': c['id'],
            'name': c['name_english'],
            'iso2': c['iso_3166_alpha2'],
            'iso3': c['iso_3166_alpha3'],
            'ehea_member': c['ehea_is_member'],
            'eqar_governmental_member_since': c['eqar_governmental_member_start'],
            'external_qaa_permitted': c['external_QAA_is_permitted__type'],
            'european_approach_permitted': c['european_approach_is_permitted__type'],
            'ehea_key_commitment': c['ehea_key_commitment__type'],
            'registered_agencies_based_here': c['agency_count'],
        }
        for c in countries.order_by('name_english').values(
            'id', 'name_english', 'iso_3166_alpha2', 'iso_3166_alpha3', 'ehea_is_member',
            'eqar_governmental_member_start', 'external_QAA_is_permitted__type',
            'european_approach_is_permitted__type', 'ehea_key_commitment__type', 'agency_count')
    ]
    return { 'total': len(results), 'results': results }


def get_country(
    country: CountryRef,
    sections: Annotated[Optional[list[CountrySection]], Field(
        max_length=6, description='Parts of the country profile to return; default: all')] = None,
    include_history: Annotated[bool, Field(
        description='Also return regulations and requirements that are no longer valid')] = False,
) -> dict:
    """
    Country knowledge base: the external quality assurance (QA) framework of a higher education system.

    Sections:
    - overview: EQAR/EHEA membership, whether institutions may use an EQAR-registered agency from abroad
      (external_QAA_is_permitted), whether the European Approach for joint programmes is permitted, general notes
      on QA requirements, Lisbon Recognition Convention and qualifications framework dates, report counts.
    - qaa_regulations: national legal acts on external QA that apply country-wide.
    - qa_requirements: per group of institution types, the external QA reviews institutions must undergo. Within a
      group, combination_logic AND means all requirements apply cumulatively, OR means they are alternatives.
      Each requirement names the ESG activity group (type of review), cycle duration in months, whether it applies
      only initially, its scope (QF-EHEA levels, fields of education, full degrees, micro-credentials),
      cross-border QA (cbqa_*: whether, with which approval and on what criteria a foreign EQAR-registered agency
      may carry it out, and whether its outcome is recognised) and use of the European Approach (ea_*). Group-
      specific regulations are listed with the group.
    - outgoing_tne: per group, whether and under which conditions/approval/QA institutions may offer transnational
      education (TNE) abroad.
    - microcredentials: per group, whether institutions may award micro-credentials, credit limit and QA regime.
    - incoming_tne: rules for foreign providers offering TNE in the country, by origin group.

    Absent fields have no data recorded.
    """
    found = resolvers.resolve_country(country)
    obj = CountryDetail().get_queryset().get(pk=found.pk)
    request = public_request(history='true' if include_history else None)
    data = collapse_controlled_lists(CountryDetailSerializer(obj, context={'request': request}).data)

    sections = set(sections or CountrySection.__args__)
    result = {
        'country': { 'id': data['id'], 'name': data['name_english'], 'iso2': data['iso_3166_alpha2'],
                     'iso3': data['iso_3166_alpha3'] },
    }
    if 'overview' in sections:
        result['overview'] = { f: data[f] for f in COUNTRY_OVERVIEW_FIELDS }
    if 'qaa_regulations' in sections:
        result['qaa_regulations'] = data['qaa_regulations']

    group_fields = [ f for section, fields in COUNTRY_GROUP_SECTIONS.items() if section in sections for f in fields ]
    if group_fields:
        eter_categories = dict(CountryInstitutionType.ETER_CATEGORY_STANDARD_CHOICES)
        result['qa_requirement_groups'] = []
        for group in data['qa_requirement_groups']:
            for requirement in group['requirements']:
                # empty scope means: no restriction
                requirement['qf_ehea_levels'] = requirement['qf_ehea_levels'] or 'all levels'
                requirement['fields_of_education'] = requirement['fields_of_education'] or 'all fields'
            result['qa_requirement_groups'].append({
                'id': group['id'],
                'institution_types': [
                    {
                        'name_national': t['name_national'],
                        'name_english': t['name_english'],
                        'category': eter_categories.get(t['eter_category_standard']),
                    }
                    for t in group['institution_types']
                ],
                **{ f: group[f] for f in group_fields },
            })

    if 'incoming_tne' in sections:
        result['incoming_tne_regulations'] = data['incoming_tne_regulations']
    return result


# --- agencies ---

AgencyInclude = Literal['activities', 'focus_countries', 'decisions', 'names']


def search_agencies(
    query: Annotated[Optional[str], Field(max_length=200, description='Part of the agency name or acronym')] = None,
    based_in: OptionalCountryRef = None,
    operates_in: Annotated[Optional[str], Field(
        min_length=1, max_length=100,
        description='Only agencies that currently have this country as a focus country (where they carry out '
                    'reviews); country by DEQAR ID, ISO code or English name')] = None,
    registered: Annotated[Literal['registered', 'not_registered', 'all'], Field(
        description='EQAR registration status')] = 'registered',
    activity_group_id: Annotated[Optional[int], Field(
        ge=1, description='Only agencies carrying out activities of this ESG activity group')] = None,
    limit: Limit = settings.MCP_DEFAULT_LIMIT,
    offset: Offset = 0,
) -> dict:
    """
    Search quality assurance agencies in DEQAR, by default those currently registered on EQAR (i.e. found to
    comply with the ESG). With operates_in, each agency is marked whether that country is an official one for it
    (agency is part of that country's national QA system) or a cross-border one. Use get_agency for details.
    """
    agencies = Agency.objects.all()
    if registered != 'all':
        agencies = agencies.filter(is_registered=(registered == 'registered'))
    if query:
        agencies = agencies.filter(Q(acronym_primary__icontains=query) | Q(name_primary__icontains=query) |
                                   Q(agencyname__agencynameversion__acronym__icontains=query) |
                                   Q(agencyname__agencynameversion__name__icontains=query))
    if based_in:
        agencies = agencies.filter(country=resolvers.resolve_country(based_in))
    focus_country = None
    if operates_in:
        focus_country = resolvers.resolve_country(operates_in)
        agencies = agencies.filter(Q(agencyfocuscountry__country=focus_country) & (
            Q(agencyfocuscountry__country_valid_to__isnull=True) |
            Q(agencyfocuscountry__country_valid_to__gte=datetime.date.today())
        ))
    if activity_group_id:
        agencies = agencies.filter(agencyesgactivity__activity_group_id=activity_group_id)

    agencies = agencies.distinct().order_by('acronym_primary')
    total = agencies.count()
    rows = list(agencies[offset:offset + limit].values(
        'id', 'acronym_primary', 'name_primary', 'country__name_english', 'is_registered', 'registration_valid_to'))

    focus = {}
    if focus_country:
        focus = {
            f['agency_id']: f
            for f in AgencyFocusCountry.objects.filter(agency_id__in=[r['id'] for r in rows], country=focus_country)
                .values('agency_id', 'country_is_official', 'country_is_crossborder')
        }

    results = []
    for row in rows:
        result = {
            'id': row['id'],
            'acronym': row['acronym_primary'],
            'name': row['name_primary'],
            'based_in': row['country__name_english'],
            'registered': row['is_registered'],
            'registration_valid_to': row['registration_valid_to'],
            'deqar_url': deqar_url('agency', row['id']),
        }
        if row['id'] in focus:
            result['official_in_country'] = focus[row['id']]['country_is_official']
            result['crossborder_in_country'] = focus[row['id']]['country_is_crossborder']
        results.append(result)
    return paginated(results, total, offset, limit)


def get_agency(
    agency: Annotated[str, Field(min_length=1, max_length=200,
                                 description='Agency: DEQAR ID, current or former acronym, or name')],
    include: Annotated[Optional[list[AgencyInclude]], Field(
        max_length=4,
        description='Additional parts to return; default: activities and focus_countries. activities: ESG '
                    'activities (types of reviews) with their activity group IDs and report counts; '
                    'focus_countries: countries where the agency carries out reviews; decisions: EQAR '
                    'registration decisions; names: current and former names and acronyms')] = None,
) -> dict:
    """
    Details of a quality assurance agency: EQAR registration status and period, base country, contact website,
    description, report and institution counts, plus its ESG activities, focus countries, EQAR decisions and
    name history as requested.
    """
    obj = resolvers.resolve_agency(agency)
    include = set(include if include is not None else ['activities', 'focus_countries'])

    data = McpAgencyDetailSerializer(obj, context={'request': public_request()}).data
    names = data.pop('names')
    activities = data.pop('activities')
    decisions = data.pop('decisions')
    result = {
        'acronym': obj.acronym_primary,
        'name': obj.name_primary,
        'deqar_url': deqar_url('agency', obj.id),
        **data,
        'country': data['country']['name_english'] if data['country'] else None,
    }
    if 'names' in include:
        result['names'] = names
    if 'activities' in include:
        result['activities'] = activities
    if 'decisions' in include:
        result['decisions'] = decisions
    if 'focus_countries' in include:
        result['focus_countries'] = [
            {
                'country': f['country__name_english'],
                'iso2': f['country__iso_3166_alpha2'],
                'official': f['country_is_official'],
                'crossborder': f['country_is_crossborder'],
                'since': f['country_valid_from'],
            }
            for f in AgencyFocusCountry.objects.filter(agency=obj).filter(
                Q(country_valid_to__isnull=True) | Q(country_valid_to__gte=datetime.date.today())
            ).order_by('country__name_english').values(
                'country__name_english', 'country__iso_3166_alpha2', 'country_is_official',
                'country_is_crossborder', 'country_valid_from')
        ]
    return result


# --- institutions ---

def search_institutions(
    query: Annotated[Optional[str], Field(
        max_length=200, description='Name, acronym, city, DEQAR ID or ETER ID of the institution')] = None,
    country: OptionalCountryRef = None,
    agency: Annotated[Optional[str], Field(
        min_length=1, max_length=200,
        description='Only institutions with reports by this agency (DEQAR ID, acronym or name)')] = None,
    qf_ehea_level: Annotated[Optional[QfEheaLevel], Field(
        description='Only institutions offering programmes at this QF-EHEA level')] = None,
    other_provider: Annotated[Optional[bool], Field(
        description='true: only providers other than higher education institutions; false: only higher '
                    'education institutions')] = None,
    crossborder: Annotated[Optional[bool], Field(
        description='true: only institutions with reports by agencies from abroad')] = None,
    limit: Limit = settings.MCP_DEFAULT_LIMIT,
    offset: Offset = 0,
) -> dict:
    """
    Search higher education institutions and other providers that have at least one QA report in DEQAR. Returns
    IDs to use with get_institution and search_reports(institution=...).
    """
    params = {
        'country_id': str(resolvers.resolve_country(country).id) if country else None,
        'agency_id': str(resolvers.resolve_agency(agency).id) if agency else None,
        'qf_ehea_level': qf_ehea_level,
        'other_provider': _bool_param(other_provider),
        'crossborder': _bool_param(crossborder),
    }
    hits, total, _ = meili_search(
        'INDEX_INSTITUTIONS', query, build_institution_filters(params), limit, offset,
        attributes=['id', 'deqar_id', 'eter_id', 'name_primary', 'names', 'website_link', 'locations',
                    'qf_ehea_levels', 'agencies', 'activity_types', 'closure_date', 'is_other_provider'],
    )

    results = []
    for hit in hits:
        current_name = next((n for n in hit['names'] if n['name_valid_to'] is None), {})
        results.append({
            'id': hit['id'],
            'deqar_id': hit['deqar_id'],
            'eter_id': hit['eter_id'],
            'name': hit['name_primary'],
            'name_official': current_name.get('name_official') if current_name.get('name_official') != hit['name_primary'] else None,
            'acronym': current_name.get('acronym'),
            'locations': sorted({ f"{l['city']}, {l['country']['name_english']}" if l['city'] else l['country']['name_english']
                                  for l in hit['locations'] }),
            'website': hit['website_link'],
            'qf_ehea_levels': hit['qf_ehea_levels'],
            'reviewed_by': [ a['acronym_primary'] for a in hit['agencies'] ],
            'activity_types': hit['activity_types'],
            'closed': timestamp_to_isodate(hit['closure_date']),
            'other_provider': hit['is_other_provider'] or None,
            'deqar_url': deqar_url('institution', hit['id']),
        })
    return paginated(results, total, offset, limit)


def get_institution(
    institution: Annotated[str, Field(min_length=1, max_length=50,
                                      description='Institution: DEQAR ID (number or DEQARINSTnnnn) or ETER ID')],
) -> dict:
    """
    Details of a higher education institution or other provider: official and English names (also historical),
    identifiers, locations, founding/closure dates, QF-EHEA levels, hierarchical relationships (parent or
    constituent units) and historical relationships (mergers, splits), and its number of QA reports. Use
    search_reports(institution=...) to list its reports.
    """
    obj = resolvers.resolve_institution(institution)
    data = McpInstitutionDetailSerializer(obj, context={'request': public_request()}).data
    _, report_count, _ = meili_search('INDEX_REPORTS', '', [
        institution_report_meili_filters(obj, 'INDEX_REPORTS'),
        f'flag != "high level"',
    ], 0, 0)
    return {
        'name': obj.name_primary,
        'deqar_id': obj.deqar_id,
        'deqar_url': deqar_url('institution', obj.id),
        'report_count': report_count,
        **data,
    }


# --- reports ---

ReportSort = Literal['relevance', 'newest', 'oldest', 'expiring', 'recently_updated']

REPORT_SORT = {
    'relevance': None,
    'newest': ['valid_from:desc'],
    'oldest': ['valid_from:asc'],
    'expiring': ['valid_to_calculated:asc'],
    'recently_updated': ['updated_at:desc'],
}

REPORT_FACETS = {
    'agency.id': 'agency',
    'institutions.locations.country.id': 'country',
    'agency_esg_activities.type': 'activity_type',
    'decision': 'decision',
    'status': 'status',
}


def _report_row(hit, now):
    """
    compact summary of a report search hit
    """
    institutions = hit['institutions'] + hit['platforms']
    programmes = hit['programmes']
    return {
        'id': hit['id'],
        'agency': hit['agency']['acronym_primary'],
        'contributing_agencies': [ a['acronym_primary'] for a in hit['contributing_agencies'] ],
        'activity_type': sorted({ a['type'] for a in hit['agency_esg_activities'] }),
        'institutions': [
            {
                'id': i['id'],
                'name': i['name_primary'],
                'country': sorted({ l['country']['name_english'] for l in i['locations'] }),
            }
            for i in institutions[:MAX_LISTED_INSTITUTIONS]
        ],
        'institution_count': len(institutions) if len(institutions) > MAX_LISTED_INSTITUTIONS else None,
        'programmes': [
            ' / '.join(filter(None, [p['name_primary'], p['qf_ehea_level']]))
            for p in programmes[:MAX_LISTED_PROGRAMMES]
        ],
        'programme_count': len(programmes) if len(programmes) > MAX_LISTED_PROGRAMMES else None,
        'decision': hit['decision'],
        'status': hit['status'],
        'valid_from': timestamp_to_isodate(hit['valid_from']),
        'valid_to': timestamp_to_isodate(hit['valid_to_calculated']),
        'valid_to_estimated': hit['valid_to'] is None or None,
        'active': hit['valid_to_calculated'] is not None and hit['valid_to_calculated'] >= now,
        'crossborder': hit['crossborder'] or None,
        'flag': hit['flag'] if hit['flag'] != 'none' else None,
        'files': len(hit['report_files']),
        'deqar_url': deqar_url('report', hit['id']),
    }


def search_reports(
    query: Annotated[Optional[str], Field(
        max_length=200, description='Free text, matched against institution names and cities, and programme '
                                    'names and qualifications')] = None,
    country: Annotated[Optional[str], Field(
        min_length=1, max_length=100,
        description='Only reports on institutions located in this country (DEQAR ID, ISO code or English name)')] = None,
    agency: Annotated[Optional[str], Field(
        min_length=1, max_length=200,
        description='Only reports by this agency, as main or contributing agency (DEQAR ID, acronym or name)')] = None,
    institution: Annotated[Optional[str], Field(
        min_length=1, max_length=50,
        description='Only reports on this institution, including its constituent units and predecessors (DEQAR '
                    'ID or ETER ID)')] = None,
    activity_type: Annotated[Optional[ActivityType], Field(description='Type of the QA activity')] = None,
    activity_group_id: Annotated[Optional[int], Field(
        ge=1, description='Only reports of this ESG activity group (see get_agency or list_reference_values)')] = None,
    status: Annotated[Optional[str], Field(
        max_length=50, description="'part of obligatory EQA system' or 'voluntary'")] = None,
    decision: Annotated[Optional[str], Field(
        max_length=50, description="'positive', 'positive with conditions or restrictions', 'negative' or "
                                   "'not applicable'")] = None,
    language: Annotated[Optional[str], Field(
        max_length=50, description='Language of the report file (English name or ISO 639 code)')] = None,
    qf_ehea_level: Annotated[Optional[QfEheaLevel], Field(
        description='Only reports covering programmes at this QF-EHEA level')] = None,
    programme_type: Annotated[Optional[Literal[PROGRAMME_TYPES]], Field(
        description='Only reports covering programmes of this type')] = None,
    active_only: Annotated[bool, Field(description='Only reports that are currently valid')] = False,
    valid_in_year: Annotated[Optional[int], Field(
        ge=1990, le=2100, description='Only reports that were valid at some point in this year')] = None,
    valid_on: Annotated[Optional[datetime.date], Field(description='Only reports valid on this date')] = None,
    crossborder: Annotated[Optional[bool], Field(
        description='true: only cross-border reports, by an agency reviewing outside its home country')] = None,
    include_flagged: Annotated[bool, Field(
        description='Include reports flagged for data quality issues (low level)')] = True,
    sort: Annotated[ReportSort, Field(
        description='relevance (to query), newest/oldest (by report date), expiring (soonest end of validity '
                    'first) or recently_updated')] = 'relevance',
    include_facets: Annotated[bool, Field(
        description='Add counts of the matching reports by agency, country, activity type, decision and status')] = False,
    limit: Limit = settings.MCP_DEFAULT_LIMIT,
    offset: Offset = 0,
) -> dict:
    """
    Search external QA reports in DEQAR. Each result summarises one report: agency, activity type,
    institutions and programmes covered, decision, status (part of the obligatory national QA system or
    voluntary), validity period, and number of report files. Where a report has no end date, validity is
    estimated at 6 years (valid_to_estimated). Use limit=0 with include_facets=true to answer "how many" and
    breakdown questions cheaply. Use get_report for summary, file links and programme details.
    """
    params = {
        'country_id': str(resolvers.resolve_country(country).id) if country else None,
        'agency_id': str(resolvers.resolve_agency(agency).id) if agency else None,
        'activity_type': activity_type,
        'activity_group_id': str(activity_group_id) if activity_group_id else None,
        'status_id': str(resolvers.resolve_report_status(status).id) if status else None,
        'decision_id': str(resolvers.resolve_report_decision(decision).id) if decision else None,
        'language_id': str(resolvers.resolve_language(language).id) if language else None,
        'programme_type': programme_type,
        'active': _bool_param(active_only or None),
        'year': str(valid_in_year) if valid_in_year else None,
        'valid_on': valid_on.isoformat() if valid_on else None,
        'cross_border': _bool_param(crossborder),
        'flag': None if include_flagged else 'none',
    }
    filters = build_report_filters(params)
    if institution:
        filters.append(institution_report_meili_filters(resolvers.resolve_institution(institution), 'INDEX_REPORTS'))
    if qf_ehea_level:
        filters.append(f'programmes.qf_ehea_level = "{qf_ehea_level}"')

    hits, total, distribution = meili_search(
        'INDEX_REPORTS', query, filters, limit, offset, sort=REPORT_SORT[sort],
        attributes=['id', 'agency', 'contributing_agencies', 'agency_esg_activities', 'institutions', 'platforms',
                    'programmes', 'decision', 'status', 'flag', 'valid_from', 'valid_to', 'valid_to_calculated',
                    'crossborder', 'report_files'],
        facets=list(REPORT_FACETS) if include_facets else None,
    )

    now = int(datetime.datetime.now().timestamp())
    extra = {}
    if include_facets:
        lookups = {
            'agency.id': dict(Agency.objects.filter(id__in=[int(i) for i in distribution.get('agency.id', {})])
                              .values_list('id', 'acronym_primary')),
            'institutions.locations.country.id': dict(
                Country.objects.filter(id__in=[int(i) for i in distribution.get('institutions.locations.country.id', {})])
                .values_list('id', 'name_english')),
        }
        extra['facets'] = {
            label: _facet_counts(distribution.get(facet, {}), lookups.get(facet))
            for facet, label in REPORT_FACETS.items()
        }
    return paginated([ _report_row(hit, now) for hit in hits ], total, offset, limit, **extra)


def get_report(
    report_id: Annotated[int, Field(ge=1, description='DEQAR report ID')],
    include_programmes: Annotated[bool, Field(
        description='Include the programmes covered, with names, qualifications, levels and ECTS')] = True,
) -> dict:
    """
    Details of one external QA report: agency and ESG activities, institutions and programmes covered, decision,
    status, validity, summary, links to the report files (PDF) and other links. The report content itself is not
    available through this server; point users to the file links.
    """
    try:
        obj = Report.objects.exclude(flag_id=FLAG_HIGH_LEVEL_ID).get(pk=report_id)
    except Report.DoesNotExist:
        raise ToolInputError(f'report [{report_id}] not found')

    data = McpReportDetailSerializer(obj, context={'request': public_request()}).data
    data['deqar_url'] = deqar_url('report', obj.id)
    if data['flag'] == 'none':
        del data['flag']
    if not include_programmes:
        data['programme_count'] = len(data.pop('programmes'))
    return data


# --- reference data ---

ReferenceKind = Literal['activity_groups', 'activity_types', 'report_statuses', 'report_decisions', 'qf_ehea_levels',
                        'programme_types', 'languages', 'permission_types', 'flags']


def list_reference_values(
    kind: Annotated[ReferenceKind, Field(description='Which list of values to return')],
    query: Annotated[Optional[str], Field(
        max_length=100, description='Filter values containing this text (activity groups: also agency acronym)')] = None,
) -> dict:
    """
    Valid values for filters and fields: ESG activity groups (types of reviews, grouped across agencies, with
    the agencies carrying them out), activity types, report statuses and decisions, QF-EHEA levels, programme
    types, report languages, permission types (as used in the country knowledge base) and report flags.
    """
    if kind == 'activity_groups':
        groups = AgencyActivityGroup.objects.select_related('activity_type').order_by('activity')
        if query:
            groups = groups.filter(Q(activity__icontains=query) |
                                   Q(agencyesgactivity__agency__acronym_primary__icontains=query)).distinct()
        total = groups.count()
        values = [
            {
                'id': g.id,
                'activity': g.activity,
                'activity_type': g.activity_type.type,
                'agencies': sorted({ a.agency.acronym_primary for a in g.agencyesgactivity_set.all() }),
            }
            for g in groups.prefetch_related('agencyesgactivity_set__agency')[:MAX_REFERENCE_VALUES]
        ]
        return { 'kind': kind, 'total': total, 'values': values }

    if kind == 'programme_types':
        values = list(PROGRAMME_TYPES)
    else:
        model, field, order = {
            'activity_types': (AgencyActivityType, 'type', 'id'),
            'report_statuses': (ReportStatus, 'status', 'id'),
            'report_decisions': (ReportDecision, 'decision', 'id'),
            'qf_ehea_levels': (QFEHEALevel, 'level', 'id'),
            'languages': (Language, 'language_name_en', 'language_name_en'),
            'permission_types': (PermissionType, 'type', 'id'),
            'flags': (Flag, 'flag', 'id'),
        }[kind]
        values = list(model.objects.order_by(order).values_list(field, flat=True))
    if query:
        values = [ v for v in values if query.lower() in v.lower() ]
    return { 'kind': kind, 'total': len(values), 'values': values[:MAX_REFERENCE_VALUES] }
