import re

import pytest
from dateutil.parser import parse as parse_date

from parkings.management.commands import fill_parking_regions

from .utils import (
    call_mgmt_cmd_with_output, create_parkings_and_regions, intersects,
    intersects_with_any)


@pytest.mark.django_db
def test_fill_parking_regions_mgmt_cmd():
    (parkings, regions) = create_parkings_and_regions()

    # Clear the regions
    for parking in parkings:
        # First save without a location to prevent region being autofilled
        old_location = parking.location
        parking.location = None
        parking.region = None
        parking.save()
        # Then fill the location back, but save only location
        parking.location = old_location
        parking.save(update_fields=['location'])

    assert all(parking.region is None for parking in parkings)

    # Call the command with output streams attached
    target_block_size = 5
    (stdout, stderr) = call_the_command(target_block_size)

    # Check the results
    for parking in parkings:
        parking.refresh_from_db()
        if parking.location and intersects_with_any(parking.location, regions):
            assert parking.region is not None
            assert intersects(parking.location, parking.region)
        else:
            assert parking.region is None

    # Check the outputted lines
    block_count = len(parkings) // target_block_size
    for (n, line) in enumerate(stdout.splitlines(), 1):
        match = re.match(
            r'^Processing block +(\d+)/ *(\d+), size +(\d+), ([^.]*)(\.+)$',
            line)
        assert match, 'Invalid output line {}: {!r}'.format(n, line)
        assert match.group(1) == str(n)
        assert match.group(2) == str(block_count)
        assert 0 <= int(match.group(3)) <= len(parkings)
        (start_str, end_str) = match.group(4).split('--')
        block_start = parse_date(start_str)
        block_end = parse_date(end_str)
        assert block_start <= block_end
        assert len(match.group(5)) == len(regions) // 10
    assert stderr == ''

    # Check that the command doesn't do anything if all parkings with a
    # location have region filled
    for parking in parkings:
        if not parking.region:
            parking.location = None
            parking.save()
    (stdout, stderr) = call_the_command(target_block_size)
    assert stdout == 'Nothing to do\n'
    assert stderr == ''

    # And finally check that it doesn't print anything when verbosity=0
    (stdout, stderr) = call_the_command(target_block_size, verbosity=0)
    assert stdout == ''
    assert stderr == ''


def call_the_command(*args, **kwargs):
    (result, stdout, stderr) = call_mgmt_cmd_with_output(
        fill_parking_regions.Command, *args, **kwargs)
    assert result is None
    return (stdout, stderr)
