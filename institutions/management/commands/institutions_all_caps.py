import re
from django.core.management import BaseCommand

from institutions.models import Institution


class Command(BaseCommand):
    help = 'List the institution names in caps.'

    def handle(self, *args, **options):
        for institution in Institution.objects.order_by('id').iterator():
            # if institution.name_primary.isupper():
                # print('%s - %s - %s' % (institution.id, institution.name_primary, title_except(institution.name_primary)))

            for iname in institution.institutionname_set.iterator():
                if iname.name_official.isupper():
                    print('%s - %s - %s' % (institution.id, iname.name_official, title_except(iname.name_official)))

                if iname.name_official_transliterated.isupper():
                    print('%s - %s - %s' % (institution.id, iname.name_official_transliterated,
                                            title_except(iname.name_official_transliterated)))

                if iname.name_english.isupper():
                    print('%s - %s - %s' % (institution.id, iname.name_english, title_except(iname.name_english)))



def title_except(s):
    exceptions = ['of', 'and']
    word_list = re.split(' ', s)
    final = [word_list[0].title()]
    for word in word_list[1:]:
        final.append(word.lower() if word.lower() in exceptions else word.title())
    return " ".join(final)