# MCP server (mcpapi app), served by a separate process: python manage.py runmcp

# public base URL of the API host, used to make report file links absolute
MCP_PUBLIC_BASE_URL = 'http://localhost:8000'

# templates for public links to DEQAR records, added to results as deqar_url
MCP_LINK_TEMPLATES = {
    'report': 'https://data.deqar.eu/report/%s',
    'agency': 'https://data.deqar.eu/agency/%s',
    'institution': 'https://data.deqar.eu/institution/%s',
}

# Host (and Origin) header values accepted by the MCP endpoint (DNS rebinding protection);
# entries may end in ':*' to allow any port - empty list disables the check
MCP_ALLOWED_HOSTS = []
MCP_ALLOWED_ORIGINS = []

# default bind address of runmcp
MCP_HOST = '0.0.0.0'
MCP_PORT = 8001

# result size limits
MCP_DEFAULT_LIMIT = 10
MCP_MAX_LIMIT = 50
MCP_MAX_OFFSET = 1000
MCP_TEXT_MAX_CHARS = 4000

# protection of database and search engine
MCP_MAX_CONCURRENCY = 8         # tool calls executed in parallel per process
MCP_STATEMENT_TIMEOUT = 10000   # PostgreSQL statement timeout (ms)
MCP_MEILI_TIMEOUT = 10          # Meilisearch request timeout (s)
