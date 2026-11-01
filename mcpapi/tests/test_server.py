import json
import os
import sys

from asgiref.sync import async_to_sync
from django.conf import settings
from django.test import SimpleTestCase
from mcp import Client, StdioServerParameters

from mcpapi.server import TOOLS, build_server
from mcpapi.tools import PROGRAMME_TYPES


class ServerProtocolTest(SimpleTestCase):
    """
    MCP protocol level, in-process - tool functions run in worker threads outside the test transaction, so only
    calls that do not need database records are made here
    """

    def server(self):
        return build_server()

    def run_client(self, fn):
        async def session():
            async with Client(self.server()) as client:
                return await fn(client)
        return async_to_sync(session)()

    def test_list_tools(self):
        result = self.run_client(lambda client: client.list_tools())
        self.assertEqual(len(result.tools), len(TOOLS))
        for tool in result.tools:
            self.assertTrue(tool.annotations.read_only_hint, tool.name)
            self.assertFalse(tool.annotations.destructive_hint, tool.name)
            self.assertFalse(tool.description.startswith(' '), tool.name)

    def test_call_tool(self):
        result = self.run_client(lambda client: client.call_tool('list_reference_values', {'kind': 'programme_types'}))
        self.assertFalse(result.is_error)
        self.assertEqual(json.loads(result.content[0].text)['values'], list(PROGRAMME_TYPES))

    def test_argument_validation(self):
        result = self.run_client(lambda client: client.call_tool('search_reports', {'limit': 500}))
        self.assertTrue(result.is_error)
        result = self.run_client(lambda client: client.call_tool('search_reports', {'activity_type': 'bogus'}))
        self.assertTrue(result.is_error)


class StdioTransportTest(ServerProtocolTest):
    """
    the same protocol tests against `manage.py runmcp --transport stdio` in a subprocess, which also proves that
    nothing but the protocol is written to stdout - the subprocess uses the regular, not the test database
    """

    def server(self):
        return StdioServerParameters(command=sys.executable,
                                     args=['manage.py', 'runmcp', '--transport', 'stdio'],
                                     cwd=str(settings.BASE_DIR), env=dict(os.environ))
