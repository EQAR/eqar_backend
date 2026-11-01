import datetime
import json
import re

from bs4 import BeautifulSoup
from django.conf import settings

# keys never returned to clients: links to the authenticated Web API and internal sort keys
DROP_KEYS = {'url', 'agency_url', 'country_url', 'name_sort'}

TRUNCATION_MARK = ' […truncated]'

HTML_TAG = re.compile(r'</?(p|br|b|i|u|strong|em|ul|ol|li|a|div|span|h[1-6]|table|tr|td)\b[^>]*>', re.IGNORECASE)
HTML_PARAGRAPHS = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
HTML_LINES = ['li', 'tr']


def is_empty(value):
    return value is None or (isinstance(value, (str, list, tuple, dict)) and len(value) == 0)


def html_to_text(text):
    """
    convert rich-text (HTML) fields to plain text, keeping paragraphs, list items and link targets
    """
    if not HTML_TAG.search(text):
        return text
    soup = BeautifulSoup(text, 'html.parser')
    for a in soup.find_all('a', href=True):
        if a['href'] not in a.get_text():
            a.append(f' ({a["href"]})')
    for br in soup.find_all('br'):
        br.replace_with('\n')
    for li in soup.find_all('li'):
        li.insert(0, '- ')
    for block in soup.find_all(HTML_PARAGRAPHS):
        block.append('\n\n')
    for block in soup.find_all(HTML_LINES):
        block.append('\n')
    lines = [ re.sub(r'[ \t\xa0]+', ' ', line).strip() for line in soup.get_text().splitlines() ]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()


def truncate(text):
    """
    cap long free-text fields at MCP_TEXT_MAX_CHARS
    """
    if len(text) > settings.MCP_TEXT_MAX_CHARS:
        return text[:settings.MCP_TEXT_MAX_CHARS] + TRUNCATION_MARK
    return text


def prune(obj):
    """
    recursively drop empty values and DROP_KEYS, convert HTML to text and truncate long strings - False and 0
    are kept
    """
    if isinstance(obj, dict):
        pruned = {}
        for key, value in obj.items():
            if key in DROP_KEYS:
                continue
            value = prune(value)
            if not is_empty(value):
                pruned[key] = value
        return pruned
    elif isinstance(obj, (list, tuple)):
        return [ v for v in (prune(i) for i in obj) if not is_empty(v) ]
    elif isinstance(obj, str):
        return truncate(html_to_text(obj))
    else:
        return obj


def to_json(obj):
    """
    compact JSON representation of a pruned tool result
    """
    return json.dumps(prune(obj), ensure_ascii=False, separators=(',', ':'), default=str)


def timestamp_to_isodate(timestamp):
    """
    convert Unix timestamp (as stored in Meilisearch) to ISO format date
    """
    return datetime.date.fromtimestamp(timestamp).isoformat() if timestamp is not None else None


def deqar_url(kind, pk):
    """
    public link to a DEQAR record, or None if no template is configured for its kind
    """
    if template := settings.MCP_LINK_TEMPLATES.get(kind):
        return template % pk
    return None


def collapse_controlled_lists(obj):
    """
    replace serialized controlled list entries (id, title, uri, description) by their title, or by title and
    description if the latter is set
    """
    if isinstance(obj, dict):
        if set(obj.keys()) == {'id', 'title', 'uri', 'description'}:
            if obj['description']:
                return { 'title': obj['title'], 'description': obj['description'] }
            return obj['title']
        return { k: collapse_controlled_lists(v) for k, v in obj.items() }
    elif isinstance(obj, (list, tuple)):
        return [ collapse_controlled_lists(i) for i in obj ]
    else:
        return obj


def paginated(results, total, offset, limit, **extra):
    """
    envelope for list results
    """
    return {
        'total': total,
        'offset': offset,
        'limit': limit,
        'next_offset': offset + limit if limit and offset + limit < total else None,
        'results': results,
        **extra,
    }
