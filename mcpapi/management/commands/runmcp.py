from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Runs the read-only DEQAR MCP server: public Streamable HTTP at /mcp (default), or STDIO for local ' \
           'clients, e.g. claude mcp add deqar -- python manage.py runmcp --transport stdio'

    def add_arguments(self, parser):
        parser.add_argument('--transport', choices=['http', 'stdio'], default='http',
                            help='http: serve via uvicorn; stdio: talk to a single client over stdin/stdout')
        parser.add_argument('--host', default=settings.MCP_HOST, help='bind address (http only)')
        parser.add_argument('--port', type=int, default=settings.MCP_PORT, help='port (http only)')
        parser.add_argument('--workers', type=int, default=1, help='number of worker processes (http only)')
        parser.add_argument('--log-level', default='info', help='uvicorn log level (http only)')

    def handle(self, *args, **options):
        if options['transport'] == 'stdio':
            self.run_stdio()
        else:
            self.run_http(options)

    def run_stdio(self):
        # stdout carries the protocol: the SDK redirects stray output to stderr while serving
        from mcpapi.server import build_server, limit_statement_time

        limit_statement_time()
        build_server().run('stdio')

    def run_http(self, options):
        import uvicorn

        uvicorn.run(
            'mcpapi.asgi:app',
            host=options['host'],
            port=options['port'],
            workers=options['workers'],
            log_level=options['log_level'],
            proxy_headers=True,
            forwarded_allow_ips='*',
            timeout_keep_alive=5,
            limit_concurrency=50,
        )
