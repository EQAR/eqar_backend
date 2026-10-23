from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from countries.models import Country, CountryInstitutionType


def eter_row(country, national=None, english=None, standard=None):
    row = {'BAS.COUNTRY': country}
    if national is not None:
        row.update({'BAS.INSTCAT': national, 'BAS.INSTCATENGL': english, 'BAS.INSTCATSTAND': standard})
    return row


ETER_ROWS = [
    eter_row('AT', 'Fachhochschule', 'University of applied sciences', 2),
    eter_row('AT', 'Fachhochschule', 'University of applied sciences', 2),
    eter_row('AT', 'Privathochschule', 'Private university', 1),
    eter_row('AT', 'Privathochschule', 'private university', 0),
    eter_row('AT', 'Privathochschule', 'Private university', 0),
    eter_row('AT', 'm', 'm', 'm'),
    eter_row('AT'),
    eter_row('UK', 'University', 'University', 1),
    eter_row('ZZ', 'Something', 'Something', 0),
]


class EterSyncInstitutionTypesTestCase(TestCase):
    fixtures = [
        'flag',
        'permission_type',
        'country',
    ]

    def run_command(self, rows, *args):
        response = mock.Mock()
        response.json.return_value = rows
        with mock.patch('countries.management.commands.eter_sync_institution_types.requests.post',
                        return_value=response):
            out = StringIO()
            call_command('eter_sync_institution_types', *args, stdout=out)
            return out.getvalue()

    def test_sync_creates_types(self):
        out = self.run_command(ETER_ROWS)
        austria = Country.objects.get(iso_3166_alpha2='AT')
        self.assertEqual(CountryInstitutionType.objects.count(), 3)
        self.assertEqual(austria.institution_types.count(), 2)

        phs = austria.institution_types.get(name_national='Privathochschule')
        self.assertEqual(phs.name_english, 'Private university')
        self.assertEqual(phs.eter_category_standard, 0)
        self.assertEqual(phs.eter_institution_count, 3)
        self.assertIn('mixed INSTCATSTAND', out)

        uk = CountryInstitutionType.objects.get(name_national='University')
        self.assertEqual(uk.country.iso_3166_alpha2, 'GB')
        self.assertIn('Unknown ETER country code: ZZ', out)

    def test_resync_unchanged_and_deactivate(self):
        self.run_command(ETER_ROWS)
        out = self.run_command(ETER_ROWS)
        self.assertIn('0 created, 0 updated, 3 unchanged, 0 deactivated', out)

        rows = [r for r in ETER_ROWS if r.get('BAS.INSTCAT') != 'Fachhochschule']
        self.run_command(rows)
        fh = CountryInstitutionType.objects.get(name_national='Fachhochschule')
        self.assertFalse(fh.is_active)

        self.run_command(ETER_ROWS)
        fh.refresh_from_db()
        self.assertTrue(fh.is_active)

    def test_country_filter_limits_deactivation(self):
        self.run_command(ETER_ROWS)
        self.run_command([eter_row('UK', 'University', 'University', 1)], '--country', 'UK')
        self.assertEqual(CountryInstitutionType.objects.filter(is_active=True).count(), 3)

    def test_dry_run(self):
        out = self.run_command(ETER_ROWS, '--dry-run')
        self.assertIn('[DRY RUN]', out)
        self.assertEqual(CountryInstitutionType.objects.count(), 0)
