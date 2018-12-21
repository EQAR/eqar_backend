import re
from django.core.management import BaseCommand

from institutions.models import Institution


class Command(BaseCommand):
    help = 'List the institution names in caps.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--save',
            action='store_true',
            dest='save',
            help='Save the modifications as well.',
        )

    def handle(self, *args, **options):
        for institution in Institution.objects.order_by('id').iterator():
            for iname in institution.institutionname_set.iterator():
                if iname.name_official.isupper():
                    print('%s - %s - %s' % (institution.id, iname.name_official, title_except(iname.name_official)))
                    if options['save']:
                        iname.name_official = title_except(iname.name_official)
                        iname.save()

                if iname.name_official_transliterated.isupper():
                    print('%s - %s - %s' % (institution.id, iname.name_official_transliterated,
                                            title_except(iname.name_official_transliterated)))
                    if options['save']:
                        iname.name_official_transliterated = title_except(iname.name_official_transliterated)
                        iname.save()

                if iname.name_english.isupper():
                    print('%s - %s - %s' % (institution.id, iname.name_english, title_except(iname.name_english)))
                    if options['save']:
                        iname.name_english = title_except(iname.name_english)
                        iname.save()

                for iname_version in iname.institutionnameversion_set.iterator():
                    if iname_version.name.isupper():
                        print('%s - %s - %s' % (institution.id, iname_version.name, title_except(iname_version.name)))
                        if options['save']:
                            iname_version.name = title_except(iname_version.name)
                            iname_version.save()

                    if iname_version.transliteration.isupper():
                        print('%s - %s - %s' % (institution.id, iname_version.transliteration,
                                                title_except(iname_version.transliteration)))
                        if options['save']:
                            iname_version.name = title_except(iname_version.transliteration)
                            iname_version.save()


def title_except(s):
    exceptions = ['of', 'and']
    word_list = re.split(' ', s)
    final = [word_list[0].title()]
    for word in word_list[1:]:
        final.append(word.lower() if word.lower() in exceptions else word.title())
    return " ".join(final)