import re

from django.db import migrations


# target PKs are those of lists/fixtures/country_qa_lists.yaml, seeded by lists/0010

# lists.PermissionType -> lists.CrossBorderPossibility: yes -> 'Allowed for all cases', no -> 'Not possible';
# 'partially / with conditions' cannot be mapped and is left empty
CBQA_POSSIBLE_MAP = {1: 3, 2: 1}

# lists.PermissionType -> lists.EuropeanApproachPossibility: yes -> 'Yes, without restrictions',
# partially -> 'Yes, subject to conditions', no -> 'No'
EA_POSSIBLE_MAP = {1: 1, 3: 2, 2: 3}

# countries.CountryQARequirementType 'institutional level': no programme scope, hence no European Approach -
# unless the country has no programme-level requirements at all, then the EA information is copied regardless
LEGACY_TYPE_INSTITUTIONAL = 1

LEGACY_CBQA_FIELDS = (
    ('eligibility', 'Eligibility'),
    ('conditions', 'Conditions'),
    ('recognition', 'Recognition'),
    ('external_QAA_note', 'Note'),
)


def has_text(value):
    """
    Checks whether a (possibly HTML) text has any content, e.g. '<p><br></p>' does not.
    """
    if not value:
        return False
    return bool(re.sub(r'<[^>]*>|&nbsp;', '', value).strip())


def legacy_cbqa_note(country):
    parts = []
    for field, label in LEGACY_CBQA_FIELDS:
        value = getattr(country, field)
        if has_text(value):
            parts.append(f'<p><strong>{label}:</strong></p>\n{value.strip()}')
    return '\n'.join(parts)


def title_prefix(title):
    return title.strip().rstrip(' .:')


def prefix_title(title, note):
    """
    Prepends the legacy requirement title to its note, e.g. 'Institutional accreditation: granted for 6 years'.
    """
    prefix = title_prefix(title)
    if not prefix:
        return note
    if not has_text(note):
        return prefix
    tag = re.match(r'\s*<p[^>]*>', note)
    if tag:
        return f'{note[:tag.end()]}{prefix}: {note[tag.end():]}'
    return f'{prefix}: {note.strip()}'


def remove_title(title, note):
    """
    Reverses prefix_title(), if the note starts with the title.
    """
    prefix = title_prefix(title)
    if not prefix:
        return note
    if note == prefix:
        return ''
    tag = re.match(r'\s*<p[^>]*>', note)
    if tag and note[tag.end():].startswith(f'{prefix}: '):
        return note[:tag.end()] + note[tag.end() + len(prefix) + 2:]
    if note.startswith(f'{prefix}: '):
        return note[len(prefix) + 2:]
    return note


def group_legacy_requirements(apps, schema_editor):
    """
    Creates one default QA requirements group per country, covering all its institution types, and assigns the
    country's legacy requirements to it. Legacy titles are prepended to the requirement notes. Country-level
    information on cross-border QA and the European Approach is copied down to each requirement.
    """
    Country = apps.get_model('countries', 'Country')
    CountryInstitutionType = apps.get_model('countries', 'CountryInstitutionType')
    CountryQARequirement = apps.get_model('countries', 'CountryQARequirement')
    CountryQARequirementGroup = apps.get_model('countries', 'CountryQARequirementGroup')

    countries = Country.objects.filter(
        id__in=CountryQARequirement.objects.filter(group__isnull=True).values('country_id')
    ).order_by('id')

    for country in countries:
        group = CountryQARequirementGroup.objects.create(country=country)
        group.institution_types.set(CountryInstitutionType.objects.filter(country=country, is_active=True))

        cbqa_possible = CBQA_POSSIBLE_MAP.get(country.external_QAA_is_permitted_id)
        cbqa_note = legacy_cbqa_note(country)
        ea_possible = EA_POSSIBLE_MAP.get(country.european_approach_is_permitted_id)
        ea_note = country.european_approach_note.strip() if has_text(country.european_approach_note) else ''

        requirements = CountryQARequirement.objects.filter(country=country, group__isnull=True)
        has_programme_requirements = requirements.exclude(qa_requirement_type_id=LEGACY_TYPE_INSTITUTIONAL).exists()

        for requirement in requirements:
            requirement.group = group
            requirement.qa_requirement_note = prefix_title(requirement.qa_requirement, requirement.qa_requirement_note)
            if requirement.cbqa_possible_id is None:
                requirement.cbqa_possible_id = cbqa_possible
            if not requirement.cbqa_other_requirements_note:
                requirement.cbqa_other_requirements_note = cbqa_note
            if requirement.qa_requirement_type_id != LEGACY_TYPE_INSTITUTIONAL or not has_programme_requirements:
                if requirement.ea_possible_id is None:
                    requirement.ea_possible_id = ea_possible
                if not requirement.ea_note:
                    requirement.ea_note = ea_note
            requirement.save()


def restore_requirement_country(apps, schema_editor):
    """
    Restores the direct country link of requirements and removes the titles from their notes; groups and copied
    information are dropped by reversing 0015.
    """
    CountryQARequirement = apps.get_model('countries', 'CountryQARequirement')
    for requirement in CountryQARequirement.objects.filter(group__isnull=False).select_related('group'):
        requirement.country_id = requirement.group.country_id
        requirement.qa_requirement_note = remove_title(requirement.qa_requirement, requirement.qa_requirement_note)
        requirement.save(update_fields=['country', 'qa_requirement_note'])


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0015_qa_requirement_groups'),
    ]

    operations = [
        migrations.RunPython(group_legacy_requirements, restore_requirement_country),
    ]
