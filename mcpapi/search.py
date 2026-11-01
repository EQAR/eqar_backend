from django.conf import settings

from eqar_backend.meilisearch import MeiliClient

from mcpapi.exceptions import ToolInputError


def meili_search(index, query, filters, limit, offset, sort=None, attributes=None, facets=None):
    """
    Search a Meilisearch index (attribute name of MeiliClient, e.g. 'INDEX_REPORTS') with page-based pagination,
    which yields exact total counts. Returns (hits, total, facet distribution).
    """
    if limit and offset % limit:
        raise ToolInputError('offset must be a multiple of limit - use next_offset from the previous page')

    meili = MeiliClient()
    meili.meili.config.timeout = settings.MCP_MEILI_TIMEOUT

    params = {
        'filter': filters,
        'hitsPerPage': limit,
        'page': offset // limit + 1 if limit else 1,
    }
    if sort:
        params['sort'] = sort
    if attributes:
        params['attributesToRetrieve'] = attributes
    if facets:
        params['facets'] = facets

    response = meili.meili.index(getattr(meili, index)).search(query or '', opt_params=params)
    return response['hits'], response['totalHits'], response.get('facetDistribution', {})
