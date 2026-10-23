from collections import Counter, defaultdict
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db import transaction

from countries.models import Country, CountryInstitutionType


class Command(BaseCommand):
    help = 'Fetch national institutional categories (BAS.INSTCAT) from ETER and update country institution types'

    # ETER special codes for missing/not applicable/confidential values
    ETER_MISSING_CODES = {'m', 'a', 'x', 'xc', 'xr', 'nc', 'c', 's'}

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', '-n', action='store_true',
                            help='Report changes without writing to the database')
        parser.add_argument('--country', action='append', dest='countries', metavar='CODE',
                            help='Limit to this ETER country code (e.g. AT, UK); can be repeated')

    def _is_missing(self, value):
        return value is None or (isinstance(value, str) and (value.strip() == '' or value.strip() in self.ETER_MISSING_CODES))

    def _fetch(self):
        api_base = getattr(settings, "ETER_API_BASE", "https://eter-project.com/api/4.0/")
        request_timeout = getattr(settings, "ETER_REQUEST_TIMEOUT", 120)
        response = requests.post(
            urljoin(api_base, 'HEIs/query/flattened'),
            json={
                'fieldIds': ['BAS.COUNTRY', 'BAS.INSTCAT', 'BAS.INSTCATENGL', 'BAS.INSTCATSTAND'],
                'filter': {},
            },
            timeout=request_timeout
        )
        response.raise_for_status()
        return response.json()

    def _aggregate(self, rows, only_countries):
        """
        Group ETER rows by (country, national category) and count English labels and standard categories.
        """
        categories = defaultdict(lambda: {'count': 0, 'english': Counter(), 'english_spelling': defaultdict(Counter), 'standard': Counter()})
        seen_countries = set()
        for row in rows:
            country = row.get('BAS.COUNTRY')
            if self._is_missing(country):
                continue
            country = country.strip().upper()
            if only_countries and country not in only_countries:
                continue
            seen_countries.add(country)
            name_national = row.get('BAS.INSTCAT')
            if self._is_missing(name_national):
                continue
            cat = categories[(country, name_national.strip())]
            cat['count'] += 1
            name_english = row.get('BAS.INSTCATENGL')
            if not self._is_missing(name_english):
                name_english = name_english.strip()
                cat['english'][name_english.lower()] += 1
                cat['english_spelling'][name_english.lower()][name_english] += 1
            standard = row.get('BAS.INSTCATSTAND')
            if isinstance(standard, int) and not isinstance(standard, bool):
                cat['standard'][standard] += 1
        return categories, seen_countries

    def _resolve(self, country, name_national, cat):
        """
        Pick the most frequent English label and standard category, warning if values are mixed.
        """
        name_english = ''
        if cat['english']:
            key = cat['english'].most_common(1)[0][0]
            name_english = cat['english_spelling'][key].most_common(1)[0][0]
            if len(cat['english']) > 1:
                variants = ', '.join(f'"{cat["english_spelling"][k].most_common(1)[0][0]}" ({n})'
                                     for k, n in cat['english'].most_common())
                self.stdout.write(self.style.WARNING(
                    f'{country} "{name_national}": mixed English labels {variants}, using "{name_english}"'))
        standard = None
        if cat['standard']:
            standard = cat['standard'].most_common(1)[0][0]
            if len(cat['standard']) > 1:
                variants = ', '.join(f'{k} ({n})' for k, n in cat['standard'].most_common())
                self.stdout.write(self.style.WARNING(
                    f'{country} "{name_national}": mixed INSTCATSTAND {variants}, using {standard}'))
        return name_english, standard

    def _country_map(self):
        country_map = {}
        for country in Country.objects.all():
            if country.iso_3166_alpha2:
                country_map.setdefault(country.iso_3166_alpha2.upper(), country)
        # OrgReg/EU codes (e.g. UK, EL) take precedence over ISO codes
        for country in Country.objects.exclude(orgreg_eu_2_letter_code=None):
            country_map[country.orgreg_eu_2_letter_code.upper()] = country
        return country_map

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        only_countries = {c.strip().upper() for c in options['countries']} if options['countries'] else None

        try:
            rows = self._fetch()
        except requests.RequestException as e:
            raise CommandError(f'Error fetching data from ETER: {e}')
        if not isinstance(rows, list):
            raise CommandError('Unexpected response from ETER: expected a list of records')

        categories, seen_countries = self._aggregate(rows, only_countries)
        country_map = self._country_map()

        for code in sorted(seen_countries - set(country_map)):
            self.stdout.write(self.style.WARNING(f'Unknown ETER country code: {code}, skipped'))

        stats = Counter()
        with transaction.atomic():
            seen_ids = defaultdict(set)
            for (code, name_national), cat in sorted(categories.items()):
                country = country_map.get(code)
                if country is None:
                    continue
                name_english, standard = self._resolve(code, name_national, cat)
                values = {
                    'name_english': name_english,
                    'eter_category_standard': standard,
                    'eter_institution_count': cat['count'],
                    'is_active': True,
                }
                try:
                    obj = CountryInstitutionType.objects.get(country=country, name_national=name_national)
                except CountryInstitutionType.DoesNotExist:
                    obj = CountryInstitutionType.objects.create(country=country, name_national=name_national, **values)
                    stats['created'] += 1
                    self.stdout.write(f'{code}: created "{name_national}" - "{name_english}" [{standard}]')
                else:
                    changed = [f for f, v in values.items() if getattr(obj, f) != v]
                    if changed:
                        for f in changed:
                            setattr(obj, f, values[f])
                        obj.save()
                        stats['updated'] += 1
                        self.stdout.write(f'{code}: updated "{name_national}" ({", ".join(changed)})')
                    else:
                        stats['unchanged'] += 1
                seen_ids[country.id].add(obj.id)

            # deactivate categories no longer in ETER, only for countries present in the response
            for code in seen_countries:
                country = country_map.get(code)
                if country is None:
                    continue
                stale = CountryInstitutionType.objects.filter(country=country, is_active=True) \
                    .exclude(id__in=seen_ids[country.id])
                for obj in stale:
                    self.stdout.write(self.style.WARNING(f'{code}: deactivated "{obj.name_national}"'))
                    stats['deactivated'] += 1
                stale.update(is_active=False)

            if dry_run:
                transaction.set_rollback(True)

        summary = ', '.join(f'{stats[k]} {k}' for k in ('created', 'updated', 'unchanged', 'deactivated'))
        self.stdout.write(self.style.SUCCESS(
            f'{"[DRY RUN] " if dry_run else ""}{len(rows)} ETER records, {len(seen_countries)} countries: {summary}'))
