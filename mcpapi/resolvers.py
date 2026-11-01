import re

from django.db.models import Q

from agencies.models import Agency
from countries.models import Country
from institutions.models import Institution
from lists.models import Language
from reports.models import ReportStatus, ReportDecision

from mcpapi.exceptions import ToolInputError

MAX_CANDIDATES = 5


def _single(queryset, value, kind, label, hint=''):
    """
    return the only object in queryset, or raise ToolInputError listing candidates
    """
    candidates = list(queryset.distinct()[:MAX_CANDIDATES + 1])
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) == 0:
        raise ToolInputError(f'unknown {kind} [{value}]{hint}')
    else:
        listed = '; '.join(label(c) for c in candidates[:MAX_CANDIDATES])
        more = ', ...' if len(candidates) > MAX_CANDIDATES else ''
        raise ToolInputError(f'ambiguous {kind} [{value}], candidates: {listed}{more} - please use an ID')


def resolve_country(value):
    """
    country by ID, ISO 3166 alpha-2/alpha-3 code or English name (exact, then unique partial match)
    """
    value = str(value).strip()
    countries = Country.objects.all()
    if value.isdecimal():
        match = countries.filter(pk=int(value))
    elif len(value) == 2:
        match = countries.filter(iso_3166_alpha2__iexact=value)
    elif len(value) == 3:
        match = countries.filter(Q(iso_3166_alpha3__iexact=value) | Q(name_english__iexact=value))
    else:
        match = countries.filter(name_english__iexact=value)
    if not value.isdecimal() and not match.exists():
        match = countries.filter(name_english__icontains=value)
    return _single(match, value, 'country', lambda c: f'{c.name_english} (id {c.id}, {c.iso_3166_alpha2})',
                   ' - use list_countries to see valid countries')


def resolve_agency(value):
    """
    agency by ID, current or former acronym, or (unique partial match of) name
    """
    value = str(value).strip()
    agencies = Agency.objects.all()
    if value.isdecimal():
        match = agencies.filter(pk=int(value))
    else:
        match = agencies.filter(acronym_primary__iexact=value)
        if not match.exists():
            match = agencies.filter(agencyname__agencynameversion__acronym__iexact=value)
        if not match.exists():
            match = agencies.filter(Q(name_primary__icontains=value) |
                                    Q(agencyname__agencynameversion__name__icontains=value))
    return _single(match, value, 'agency', lambda a: f'{a.acronym_primary} (id {a.id}): {a.name_primary}',
                   ' - use search_agencies to find agencies')


def resolve_institution(value):
    """
    institution by ID, DEQAR ID (DEQARINSTnnnn) or ETER ID
    """
    value = str(value).strip()
    institutions = Institution.objects.all()
    if value.isdecimal():
        match = institutions.filter(pk=int(value))
    elif re.fullmatch(r'DEQARINST(AP)?\d+', value, re.IGNORECASE):
        match = institutions.filter(deqar_id__iexact=value)
    else:
        match = institutions.filter(eter_id__iexact=value)
    return _single(match, value, 'institution', lambda i: f'{i.name_primary} (id {i.id})',
                   ' - use search_institutions to find institutions by name')


def resolve_report_status(value):
    return _single(ReportStatus.objects.filter(status__iexact=value.strip()), value, 'report status',
                   lambda s: s.status, ' - use list_reference_values(kind="report_statuses") for valid values')


def resolve_report_decision(value):
    return _single(ReportDecision.objects.filter(decision__iexact=value.strip()), value, 'report decision',
                   lambda d: d.decision, ' - use list_reference_values(kind="report_decisions") for valid values')


def resolve_language(value):
    """
    language by English name or ISO 639-1/639-2 code
    """
    value = value.strip()
    match = Language.objects.filter(Q(language_name_en__iexact=value) | Q(iso_639_1__iexact=value) |
                                    Q(iso_639_2__iexact=value))
    return _single(match, value, 'language', lambda l: f'{l.language_name_en} ({l.iso_639_1})',
                   ' - use list_reference_values(kind="languages") for valid values')
