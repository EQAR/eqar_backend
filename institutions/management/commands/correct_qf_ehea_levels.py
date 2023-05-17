from django.core.management import BaseCommand
from django.db.models import Count

from institutions.models import Institution, InstitutionQFEHEALevel

class Command(BaseCommand):
    help = 'Remove multiple InstitutionQFEHEALevel records.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', dest='dry_run',
                            help="Don't import anything, just show me a summary of what would happen.",
                            action='store_true')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        for institution in Institution.objects.iterator():
            iqfehea_levels = InstitutionQFEHEALevel.objects.filter(
                institution=institution
            ).values('qf_ehea_level__id').annotate(count=Count('qf_ehea_level__id'))
            for iqfehea_level in iqfehea_levels:
                # If there are more of the same QF-EHEA level set for an institution
                if iqfehea_level['count'] > 1:
                    # If there are only one verified one, keep that and remove the rest.
                    if InstitutionQFEHEALevel.objects.filter(
                        institution=institution,
                        qf_ehea_level__id=iqfehea_level['qf_ehea_level__id'],
                        qf_ehea_level_verified=True
                    ).count() == 1:
                        print('Removing multiple QF-EHEA Levels (%s) from %s' %
                              (iqfehea_level['qf_ehea_level__id'], institution))
                        if not dry_run:
                            InstitutionQFEHEALevel.objects.filter(
                                institution=institution,
                                qf_ehea_level__id=iqfehea_level['qf_ehea_level__id'],
                                qf_ehea_level_verified=False
                            ).delete()

                    # If there are more verified one, keep the first one and remove the rest (verified + unverified)
                    if InstitutionQFEHEALevel.objects.filter(
                        institution=institution,
                        qf_ehea_level__id=iqfehea_level['qf_ehea_level__id'],
                        qf_ehea_level_verified=True
                    ).count() > 1:
                        iqfehea_record = InstitutionQFEHEALevel.objects.filter(
                            institution=institution,
                            qf_ehea_level__id=iqfehea_level['qf_ehea_level__id'],
                            qf_ehea_level_verified=True
                        ).first()

                    # If there are multiple unverified one, keep the first one and remove the rest
                    if InstitutionQFEHEALevel.objects.filter(
                        institution=institution,
                        qf_ehea_level__id=iqfehea_level['qf_ehea_level__id'],
                        qf_ehea_level_verified=True
                    ).count() == 0:
                        iqfehea_record = InstitutionQFEHEALevel.objects.filter(
                            institution=institution,
                            qf_ehea_level__id=iqfehea_level['qf_ehea_level__id'],
                        ).first()

                    # Remove the rest
                    print('Removing multiple QF-EHEA Levels (%s) from %s' %
                          (iqfehea_level['qf_ehea_level__id'], institution))
                    if not dry_run:
                        InstitutionQFEHEALevel.objects.filter(
                            institution=institution,
                            qf_ehea_level__id=iqfehea_level['qf_ehea_level__id'],
                        ).exclude(id=iqfehea_record.id).delete()

