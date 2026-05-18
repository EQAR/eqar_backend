import csv
import datetime
import io
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import BaseCommand

from adminapi.serializers.flag_serializers import ReportFlagSerializer
from reports.models import ReportFlag


class Command(BaseCommand):
    help = 'Export flagged reports to a CSV file.'

    DEFAULT_SUBFOLDER = 'csv-export'
    DEFAULT_FILENAME = 'reports-flagged.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', dest='output', default=None,
            help='Local file to save the CSV to. If omitted, the file is saved '
                 'via the configured storage backend under MEDIA_ROOT.',
        )
        parser.add_argument(
            '--subfolder', dest='subfolder', default=self.DEFAULT_SUBFOLDER,
            help='Sub-folder (relative to MEDIA_ROOT) when saving via storage. '
                 'Default: "%s".' % self.DEFAULT_SUBFOLDER,
        )
        parser.add_argument(
            '--include-inactive', dest='include_inactive', action='store_true',
            help='Also include flags that are no longer active.',
        )

    def handle(self, *args, **options):
        output = options['output']
        subfolder = options['subfolder']
        include_inactive = options['include_inactive']

        queryset = ReportFlag.objects.all() if include_inactive \
            else ReportFlag.objects.filter(active=True)
        queryset = queryset.select_related('report', 'report__agency', 'flag') \
            .order_by('report__agency__acronym_primary', 'report_id')

        serializer = ReportFlagSerializer(queryset, many=True)
        rows = serializer.data

        if not rows:
            self.stdout.write(self.style.WARNING('No flagged reports found; nothing to export.'))
            return

        fieldnames = list(rows[0].keys())

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

        if output:
            output_path = output
            if os.path.isdir(output_path):
                output_path = os.path.join(output_path, self.DEFAULT_FILENAME)
            os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                f.write(buffer.getvalue())
            saved_to = output_path
        else:
            storage_path = os.path.join(subfolder, self.DEFAULT_FILENAME) if subfolder else self.DEFAULT_FILENAME
            if default_storage.exists(storage_path):
                default_storage.delete(storage_path)
            saved_name = default_storage.save(
                storage_path,
                ContentFile(buffer.getvalue().encode('utf-8')),
            )
            saved_to = default_storage.path(saved_name) \
                if hasattr(default_storage, 'path') else saved_name

        self.stdout.write(self.style.SUCCESS(
            'Exported %d flagged report(s) to %s' % (len(rows), saved_to)
        ))
