import json

from database_sanitizer.session import hash_text_to_ints

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
N_LETTERS = len(LETTERS)
N_DIGITS = len(DIGITS)


def sanitize_registration_number(value):
    if not value:
        return value

    normalized = value.replace('-', '').replace(' ', '').upper()

    if not normalized:
        # Return values containing only spaces or dashes (such as " ", "
        # - ", "-" and "--") as is
        return value

    ints = hash_text_to_ints(normalized, (16, 16, 16, 16, 16, 16))

    return 'X{letters}{sep}{digits}'.format(
        letters=''.join(LETTERS[x % N_LETTERS] for x in ints[0:3]),
        sep=('-' if '-' in value else ''),
        digits=''.join(DIGITS[x % N_DIGITS] for x in ints[3:6]))


def sanitize_permit_subjects(value):
    if not value or value in ('[]', '{}'):
        return value
    subjects = json.loads(value)
    for subject in subjects:
        subject['registration_number'] = sanitize_registration_number(
            subject['registration_number'])
    return json.dumps(subjects)
