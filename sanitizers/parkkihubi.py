import json

from parkings.utils import sanitizing


def sanitize_registration_number(value):
    return sanitizing.sanitize_registration_number(value, prefix='X')


def sanitize_permit_subjects(value):
    if not value or value in ('[]', '{}'):
        return value
    subjects = json.loads(value)
    for subject in subjects:
        subject['registration_number'] = sanitize_registration_number(
            subject['registration_number'])
    return json.dumps(subjects)
