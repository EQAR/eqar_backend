import pysolr
from django.conf import settings

from reports.models import Report


class InstitutionReportIndexer:
    """
    Class to index Institution and their corresponding Report records to Solr.
    """

    def __init__(self, institution):
        self.institution = institution
        self.solr_core = getattr(settings, "SOLR_CORE_INSTITUTIONS_REPORTS", "deqar-institutions-reports")
        self.solr_url = "%s/%s" % (getattr(settings, "SOLR_URL", "http://localhost:8983/solr"), self.solr_core)
        self.solr = pysolr.Solr(self.solr_url)
        self.doc = {
            'id': None,
            'eter_id': None,
            'national_identifier': None,
            'name_primary': None,
            'name_sort': None,
            'name_official': [],
            'name_official_transliterated': [],
            'name_english': [],
            'name_version': [],
            'name_version_transliterated': [],
            'country': [],
            'city': [],
            'place': [],
            # Facets
            'place_facet': [],
            'qf_ehea_level_facet': [],
            # Aggregated entries
            'aggregated_name_official': [],
            'aggregated_name_official_transliterated': [],
            'aggregated_name_english': [],
            'aggregated_name_version': [],
            'aggregated_name_version_transliterated': [],
            # Report related entries
            'has_report': False,
            'reports_agencies': []
        }

    def index(self):
        self._index_main_institution()
        self._index_hierarchical_institutions()
        self._index_reports()
        self._remove_duplicates()
        self._remove_empty_keys()
        try:
            self.solr.add([self.doc])
            print('Indexed Institution No. %s!' % self.doc['id'])
        except pysolr.SolrError as e:
            print('Error with Institution No. %s! Error: %s' % (self.doc['id'], e))

    def _index_main_institution(self):
        self.doc['id'] = self.institution.id
        self.doc['eter_id'] = self.institution.eter_id
        self.doc['national_identifier'] = self.institution.national_identifier
        self.doc['name_primary'] = self.institution.name_primary.strip()
        self.doc['name_sort'] = self.institution.name_sort.strip()
        self.doc['website_link'] = self.institution.website_link.strip()

        # Index name versions
        for iname in self.institution.institutionname_set.all():
            self.doc['name_official'].append(iname.name_official.strip())
            self.doc['name_official_transliterated'].append(iname.name_official_transliterated.strip())
            self.doc['name_english'].append(iname.name_english.strip())

            for iname_version in iname.institutionnameversion_set.all():
                self.doc['name_version'].append(iname_version.name.strip())
                self.doc['name_version_transliterated'].append(iname_version.transliteration.strip())

        self.doc['name_official'] = list(filter(None, self.doc['name_official']))
        self.doc['name_official_transliterated'] = list(filter(None, self.doc['name_official_transliterated']))
        self.doc['name_english'] = list(filter(None, self.doc['name_english']))
        self.doc['name_version'] = list(filter(None, self.doc['name_version']))
        self.doc['name_version_transliterated'] = list(filter(None, self.doc['name_version_transliterated']))

        # Index places
        for icountry in self.institution.institutioncountry_set.iterator():
            self.doc['country'].append(icountry.country.name_english.strip())
            if icountry.city:
                self.doc['city'].append(icountry.city.strip())
                self.doc['place'].append("%s (%s)" % (icountry.city.strip(),
                                                      icountry.country.name_english.strip()))
            else:
                self.doc['place'].append(icountry.country.name_english.strip())

        self.doc['place'] = list(filter(None, self.doc['place']))
        self.doc['place_facet'] = list(filter(None, self.doc['place']))

        self.doc['country'] = list(filter(None, self.doc['country']))
        self.doc['city'] = list(filter(None, self.doc['city']))

        # Index QF-EHEA level
        for iqfehealevel in self.institution.institutionqfehealevel_set.iterator():
            self.doc['qf_ehea_level_facet'].append(iqfehealevel.qf_ehea_level.level.strip())

        self.doc['qf_ehea_level_facet'] = list(filter(None, self.doc['qf_ehea_level_facet']))

    def _index_hierarchical_institutions(self):
        # Index parents
        for related_institution in self.institution.relationship_parent.iterator():
            self._index_related_institution(related_institution.institution_child)

        # Index children
        for related_institution in self.institution.relationship_child.iterator():
            self._index_related_institution(related_institution.institution_parent)

    def _index_related_institution(self, related_institution):
        # Index name versions
        aggregated_name_official = self.doc['aggregated_name_official']
        aggregated_name_official_transliterated = self.doc['aggregated_name_official_transliterated']
        aggregated_name_english = self.doc['aggregated_name_english']
        aggregated_name_version = self.doc['aggregated_name_version']
        aggregated_name_version_transliterated = self.doc['aggregated_name_version_transliterated']

        for iname in related_institution.institutionname_set.iterator():
            aggregated_name_official.append(iname.name_official.strip())
            aggregated_name_official_transliterated.append(iname.name_official_transliterated.strip())
            aggregated_name_english.append(iname.name_english.strip())

            for iname_version in iname.institutionnameversion_set.iterator():
                aggregated_name_version.append(iname_version.name.strip())
                aggregated_name_version_transliterated.append(iname_version.transliteration.strip())

        self.doc['aggregated_name_official'] = list(filter(None, aggregated_name_official))
        self.doc['aggregated_name_official_transliterated'] = list(
            filter(None, aggregated_name_official_transliterated))
        self.doc['aggregated_name_english'] = list(filter(None, aggregated_name_english))
        self.doc['aggregated_name_version'] = list(filter(None, aggregated_name_version))
        self.doc['aggregated_name_version_transliterated'] = list(filter(None, aggregated_name_version_transliterated))

    def _remove_duplicates(self):
        for k, v in self.doc.items():
            if isinstance(v, list):
                self.doc[k] = list(set(v))

    def _remove_empty_keys(self):
        new_doc = {k: v for k, v in self.doc.items() if v}
        self.doc.clear()
        self.doc.update(new_doc)

    def _index_reports(self):
        reports = Report.objects.filter(institutions=self.institution).iterator()
        self._add_reports(reports)

    def _index_related_reports(self):
        # Index parents
        for related_institution in self.institution.relationship_parent.iterator():
            reports = Report.objects.filter(institution=related_institution.institution_child).iterator()
            self._add_reports(reports)

        # Index children
        for related_institution in self.institution.relationship_child.iterator():
            reports = Report.objects.filter(institution=related_institution.institution_parent).iterator()
            self._add_reports(reports)

    def _add_reports(self, reports):
        for report in reports:
            self.doc['has_report'] = True
            self.doc['reports_agencies'].append(report.agency.acronym_primary)
