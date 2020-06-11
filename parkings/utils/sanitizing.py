from database_sanitizer import session

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
N_LETTERS = len(LETTERS)
N_DIGITS = len(DIGITS)


def reset_sanitizing_session():
    session.reset()


def sanitize_registration_number(value, prefix='!'):
    if not value:
        return value

    normalized = value.replace('-', '').replace(' ', '').upper()

    if not normalized:
        # Return values containing only spaces or dashes (such as " ", "
        # - ", "-" and "--") as is
        return value

    ints = session.hash_text_to_ints(normalized, (16, 16, 16, 16, 16, 16))

    return '{prefix}{letters}{sep}{digits}'.format(
        prefix=prefix,
        letters=''.join(LETTERS[x % N_LETTERS] for x in ints[0:3]),
        sep=('-' if '-' in value else ''),
        digits=''.join(DIGITS[x % N_DIGITS] for x in ints[3:6]))
