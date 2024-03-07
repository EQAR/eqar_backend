import os
from datetime import datetime

from django.conf import settings

from django.core.management import BaseCommand

from django.db.models import Q

from lxml import etree

from countries.models import Country
from connectapi.europass.accrediation_xml_creator_v2 import AccrediationXMLCreatorV2

class Command(BaseCommand):
    help = 'Generate XML export files for Europass/QDR.'

    def add_arguments(self, parser):
        parser.add_argument('COUNTRY', nargs='+',
                            help='The two letter ISO code of the country/-ies to export.')
        parser.add_argument('--base', '-b',
                            help='The base URL to prefix report file links with.')
        parser.add_argument('--directory', '-d', default='europass-v2',
                            help='The directory (relative to MEDIA_ROOT) where to place exported files.')
        parser.add_argument('--force', '-f',
                            help='Skip check against XSD files.', action='store_true')

    def handle(self, *args, **options):
        # make export directory
        base_dir = os.path.join(settings.MEDIA_ROOT, options['directory'])
        os.makedirs(base_dir, exist_ok=True)

        for ctry_code in options['COUNTRY']:
            try:
                country = Country.objects.get(Q(iso_3166_alpha3=ctry_code.upper()) | Q(iso_3166_alpha2__exact=ctry_code))
            except:
                self.stderr.write(f'Unknown country code: [{ctry_code}]')
            else:
                self.stdout.write(f'Generating XML file for {country}:')
                start_at = datetime.now()

                creator = AccrediationXMLCreatorV2(country, baseurl=options.get('base'), check=not options['force'])
                file_path = os.path.join(base_dir, f'{country.iso_3166_alpha2}.xml')
                with open(file_path, 'wb') as f:
                    f.write(etree.tostring(creator.create(), encoding='utf8'))

                done_at = datetime.now()
                duration = done_at - start_at

                self.stdout.write(f'  - saved as: {file_path}')
                self.stdout.write(f'  - file size: {os.path.getsize(file_path)}')
                self.stdout.write(f'  - generation time: {duration}')
                self.stdout.write(f'  - Last-Modified: {creator.last_modified}')

                os.utime(file_path, (int(done_at.timestamp()), int(creator.last_modified.timestamp())))

