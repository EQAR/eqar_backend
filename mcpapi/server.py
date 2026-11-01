import functools
import inspect
import logging
import threading

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import close_old_connections
from meilisearch.errors import MeilisearchApiError
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from rest_framework.exceptions import APIException, ValidationError

from mcpapi import tools
from mcpapi.exceptions import ToolInputError
from mcpapi.shaping import to_json

logger = logging.getLogger(__name__)

INSTRUCTIONS = """\
DEQAR, the Database of External Quality Assurance Results, is run by EQAR, the European Quality Assurance \
Register for Higher Education. It holds reports and decisions of external quality assurance (QA) reviews of \
higher education institutions and programmes, published by QA agencies registered on EQAR, and a knowledge \
base on the external QA frameworks of the countries of the European Higher Education Area (EHEA).

Key concepts:
- ESG: the Standards and Guidelines for Quality Assurance in the EHEA. Agencies registered on EQAR have been \
found to comply with the ESG; their reviews are listed in DEQAR.
- Agency: a QA agency. registered = currently on the EQAR register. Focus countries are where it carries out \
reviews; official focus countries are those whose national QA system it is part of.
- ESG activity: a type of external QA an agency carries out (e.g. programme accreditation, institutional \
audit). Activities are grouped across agencies into activity groups, and typed as institutional, programme, \
joint programme or institutional/programme.
- Report: the outcome of one review, with a decision (positive; positive with conditions or restrictions; \
negative; not applicable), a status (part of the obligatory national QA system, or voluntary) and a validity \
period. Reports without an end date are considered valid for 6 years. Cross-border reports are by an agency \
reviewing outside its home country. Reports with a low-level flag have minor data quality issues.
- Country knowledge base: which external QA institutions must undergo (QA requirements, per group of \
institution types), whether they may use a suitable EQAR-registered agency from abroad (external QAA, \
cross-border QA), whether the European Approach for joint programmes is permitted, national QA regulations, \
and rules for transnational education (TNE) and micro-credentials.

How to use the tools:
- Countries accept a DEQAR ID, ISO code or English name; agencies an ID, acronym or name; institutions a DEQAR \
or ETER ID (find them with search_institutions first).
- For "how many" or breakdown questions, call search_reports with limit=0 and include_facets=true.
- Results are paginated: pass next_offset to get the next page.
- The server holds metadata only: report PDFs are linked, not readable here.
- Cite the deqar_url links so users can check the records. DEQAR data may lag behind agencies' own records.
"""

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

TOOLS = [
    (tools.list_countries, 'List countries'),
    (tools.get_country, 'Country QA framework'),
    (tools.search_agencies, 'Search QA agencies'),
    (tools.get_agency, 'QA agency details'),
    (tools.search_institutions, 'Search institutions'),
    (tools.get_institution, 'Institution details'),
    (tools.search_reports, 'Search QA reports'),
    (tools.get_report, 'QA report details'),
    (tools.list_reference_values, 'List reference values'),
]

# limits concurrent database/search work per process; tool functions run in a thread pool
_slots = threading.BoundedSemaphore(settings.MCP_MAX_CONCURRENCY)
SLOT_TIMEOUT = 10


def tool_call(fn):
    """
    Wrap a tool function: limit concurrency, manage database connections (there are no request signals here),
    render the result as compact JSON and convert anticipated errors into messages for the model.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not _slots.acquire(timeout=SLOT_TIMEOUT):
            raise ToolError('The DEQAR server is busy, please try again shortly.')
        try:
            close_old_connections()
            return to_json(fn(*args, **kwargs))
        except ToolInputError as e:
            raise ToolError(str(e))
        except (ValidationError, DjangoValidationError) as e:
            raise ToolError(f'invalid argument: {e}')
        except APIException as e:
            raise ToolError(str(e.detail))
        except MeilisearchApiError as e:
            logger.warning('Meilisearch error in %s: %s', fn.__name__, e)
            raise ToolError('The search failed, please check the arguments or try again later.')
        finally:
            close_old_connections()
            _slots.release()
    return wrapper


def build_server():
    server = MCPServer(
        name='deqar',
        title='DEQAR',
        description='Read-only access to DEQAR, the Database of External Quality Assurance Results in the '
                    'European Higher Education Area, including the country knowledge base',
        instructions=INSTRUCTIONS,
        website_url='https://www.eqar.eu/qa-results/',
        subscriptions=False,
    )
    for fn, title in TOOLS:
        server.add_tool(tool_call(fn), title=title, description=inspect.cleandoc(fn.__doc__),
                        annotations=READ_ONLY, structured_output=False)
    return server


def limit_statement_time():
    """
    Protect the database from expensive queries - applies to this process only, call before the first connection
    """
    if settings.MCP_STATEMENT_TIMEOUT and settings.DATABASES['default'].get('ENGINE', '').endswith('postgresql'):
        options = settings.DATABASES['default'].setdefault('OPTIONS', {})
        options['options'] = f"{options.get('options', '')} -c statement_timeout={settings.MCP_STATEMENT_TIMEOUT}".strip()


def transport_security():
    if settings.MCP_ALLOWED_HOSTS:
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=settings.MCP_ALLOWED_HOSTS,
            allowed_origins=settings.MCP_ALLOWED_ORIGINS,
        )
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)
