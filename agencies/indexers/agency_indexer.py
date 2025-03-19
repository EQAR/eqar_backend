import pysolr
from django.conf import settings


class AgencyIndexer:
    """
    Class to index Agency records to Solr.
    """

    def __init__(self, agency):
        self.agency = agency
        self.solr_core = getattr(settings, "SOLR_CORE_AGENCIES", "deqar-agencies")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url, always_commit=True)
        self.doc = {
            # Display fields
            'id': None,
            'deqar_id': None,
            'acronym': None,
            'name': None,
            'country': None,
            'valid_from': None,
            'valid_to': None,

            # Search fields
            'name_search': [],
            'acronym_search': [],
            'name_version_search': [],
            'acronym_version_search': [],

            # ID Filter fields
            'country_id': [],
            'focus_country_id': [],
            'allowed_agency_id': [],

            # Sort fields
            'deqar_id_sort': None,
            'name_sort': None,
            'acronym_sort': None,

            # Facet fields
            'country_facet': [],
            'focus_country_facet': [],
            'allowed_agency_facet': []
        }

    def index(self):
        self._index_agency()
        self._remove_duplicates()
        self._remove_empty_keys()
        try:
            self.solr.add([self.doc])
            print('Indexed Agency No. %s!' % self.doc['id'])
        except pysolr.SolrError as e:
            print('Error with Agency No. %s! Error: %s' % (self.doc['id'], e))

    def _index_agency(self):
        # Index display fields
        self.doc['id'] = self.agency.id
        self.doc['deqar_id'] = self.agency.id
        self.doc['acronym'] = self.agency.acronym_primary.strip()
        self.doc['name'] = self.agency.name_primary.strip()
        self.doc['country'] = self.agency.country.name_english.strip()
        self.doc['valid_from'] = self.agency.registration_start
        self.doc['valid_to'] = self.agency.registration_valid_to

        # Index sort fields
        self.doc['deqar_id_sort'] = self.agency.id
        self.doc['name_sort'] = self.agency.name_primary.strip()
        self.doc['acronym_sort'] = self.agency.acronym_primary.strip()
        self.doc['country_sort'] = self.agency.country.name_english.strip()

        # Index name versions
        for aname in self.agency.agencyname_set.all():
            for aname_version in aname.agencynameversion_set.all():
                self.doc['name_version_search'].append(aname_version.name.strip())
                self.doc['name_version_search'].append(aname_version.name_transliterated.strip())
                self.doc['acronym_version_search'].append(aname_version.acronym.strip())
                self.doc['acronym_version_search'].append(aname_version.acronym_transliterated.strip())

        self.doc['name_version_search'] = list(filter(None, self.doc['name_version_search']))
        self.doc['acronym_version_search'] = list(filter(None, self.doc['acronym_version_search']))

        # Index facets
        self.doc['country_facet'] = self.agency.country.name_english.strip()
        self.doc['country_id'] = self.agency.country.id

        # Index focus countries
        for fcountry in self.agency.agencyfocuscountry_set.all():
            self.doc['focus_country_facet'].append(fcountry.country.name_english.strip())
            self.doc['focus_country_id'].append(fcountry.country.id)

        # Index allowed agencies
        for allowed_agency in self.agency.allowed_agency.all():
            sa = allowed_agency.submitting_agency
            if sa.agency:
                self.doc['allowed_agency_facet'].append(sa.agency.acronym_primary)
                self.doc['allowed_agency_id'].append(sa.agency.id)
            else:
                self.doc['allowed_agency_facet'].append(sa.external_agency_acronym)

    def _remove_duplicates(self):
        for k, v in self.doc.items():
            if isinstance(v, list):
                self.doc[k] = list(set(v))

    def _remove_empty_keys(self):
        new_doc = {k: v for k, v in self.doc.items() if v}
        self.doc.clear()
        self.doc.update(new_doc)
