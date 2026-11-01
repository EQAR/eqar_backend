"""
ASGI application of the DEQAR MCP server, served by `python manage.py runmcp`
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eqar_backend.settings')
django.setup()

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from mcpapi.server import build_server, limit_statement_time, transport_security

limit_statement_time()


def post_only(app):
    """
    Reject GET (server-to-client event stream) and DELETE (session termination): the server is stateless and
    never sends unsolicited messages, and open streams would tie up connections.
    """
    async def wrapper(scope, receive, send):
        if scope['type'] == 'http' and scope['method'] in ('GET', 'DELETE'):
            await Response(status_code=405, headers={'Allow': 'POST'})(scope, receive, send)
        else:
            await app(scope, receive, send)
    return wrapper


app = CORSMiddleware(
    post_only(build_server().streamable_http_app(
        streamable_http_path='/mcp',
        json_response=True,
        stateless_http=True,
        transport_security=transport_security(),
    )),
    allow_origins=['*'],
    allow_methods=['POST', 'OPTIONS'],
    allow_headers=['*'],
    expose_headers=['Mcp-Protocol-Version'],
)
