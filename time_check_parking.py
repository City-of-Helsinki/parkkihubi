#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Measure performance of the check_parking endpoint.

Make sure that you run the server in non-DEBUG mode with a real WSGI
runner like uWSGI rather than using the Django's runserver.  This can be
achieved e.g. with:

    pip install uwsgi
    uwsgi \
      --http localhost:8000 \
      --wsgi-file parkkihubi/wsgi.py \
      --env DEBUG=0 \
      --disable-logging \
      --processes 10
"""

import json
import multiprocessing
import os
import sys
import time

import requests

url = 'http://127.0.0.1:8000/enforcement/v1/check_parking/'

headers = {
    'Content-type': 'application/json',
    'Authorization': 'ApiKey {auth_token}',
}

registration_numbers = [
    'XMLB-044',  # Permit: 2019-07-02 21:00 -- 2019-09-02 20:59 / XMLB044 / A
                 #    and: 2019-09-02 21:00 -- 2019-10-02 20:59 / XMLB044 / A.
                 # No parkings.

    'XCMA-874',  # Permit: 2018-09-28 09:45 -- 2019-09-27 20:59 / XCMA874 / N.
                 # No parkings.

    'XNJL-006',  # No permits.
                 # Parkings almost every day from about 04:00Z to
                 # 12:00Z, almost all in Zone 2.

    'XFBI-872',  # No permits.
                 # Parkings from 2018-01-17 to 2019-05-22.

    'XYYY-999',  # No permits.
                 # No parkings.

    'XAAV-538',  # Permit: 2018-08-21 21:00 -- 2019-08-21 20:59 / XAAV538 / I.
                 # Parkings: 2019-01-12 12:29:26 -> 14:14:12 (Zone 2),
                 #           2019-06-26 18:24:20 -> 18:29:46 (Zone 2), and
                 #           2019-07-03 11:48:04 -> 12:00:15 (Zone 1).
]

locations = {
    name: coordinates for (coordinates, name) in [
        ((24.9205277, 60.1666692), 'Zone 1 Area A Kamppi'),
        ((24.9545280, 60.1802120), 'Zone 1 Area I Sörnäinen'),
        ((24.9589848, 60.1782987), 'Zone 1 Area - Hakaniemenranta'),
        ((24.9196850, 60.1846670), 'Zone 2 Area H Taka-Töölö'),
        ((24.8627390, 60.1492930), 'Zone - Area N Lauttasaari'),
        ((24.9271080, 60.2179880), 'Zone - Area - Pohjois-Pasila'),
        ((12.3540400, 56.0076430), 'Zone - Area - Denmark'),
    ]
}
location_by_coords = {coords: name for (name, coords) in locations.items()}

timestamps = [
    '2018-06-11T06:10:42+00:00',  # Allowed for XNJL-006

    '2019-07-03T11:50:51+00:00',  # Allowed for XMLB-044, XCMA-874, XNJL-006,
                                  # XAAV-538

    '2019-07-03T12:01:11+00:00',  # Allowed for XMLB-044, XCMA-874.
                                  # Expired less that 15 min ago for
                                  # XNJL-006, XAAV-538.

    '2019-09-27T21:12:34+00:00',  # Allowed for XMLB-044.
                                  # Expired 30s ago for XCMA-874

    '2022-10-20T12:00:00+00:00',  # No parkings or permits
]

expected_alloweds = [
    ('XAAV-538', '2019-07-03T11:50:51+00:00', 'Zone - Area - Denmark'),
    ('XAAV-538', '2019-07-03T11:50:51+00:00', 'Zone - Area - Pohjois-Pasila'),
    ('XAAV-538', '2019-07-03T11:50:51+00:00', 'Zone - Area N Lauttasaari'),
    ('XAAV-538', '2019-07-03T11:50:51+00:00', 'Zone 1 Area - Hakaniemenranta'),
    ('XAAV-538', '2019-07-03T11:50:51+00:00', 'Zone 1 Area A Kamppi'),
    ('XAAV-538', '2019-07-03T11:50:51+00:00', 'Zone 1 Area I Sörnäinen'),
    ('XAAV-538', '2019-07-03T11:50:51+00:00', 'Zone 2 Area H Taka-Töölö'),
    ('XAAV-538', '2019-07-03T12:01:11+00:00', 'Zone 1 Area I Sörnäinen'),
    ('XCMA-874', '2019-07-03T11:50:51+00:00', 'Zone - Area N Lauttasaari'),
    ('XCMA-874', '2019-07-03T12:01:11+00:00', 'Zone - Area N Lauttasaari'),
    ('XMLB-044', '2019-07-03T11:50:51+00:00', 'Zone 1 Area A Kamppi'),
    ('XMLB-044', '2019-07-03T12:01:11+00:00', 'Zone 1 Area A Kamppi'),
    ('XMLB-044', '2019-09-27T21:12:34+00:00', 'Zone 1 Area A Kamppi'),
    ('XNJL-006', '2018-06-11T06:10:42+00:00', 'Zone - Area - Denmark'),
    ('XNJL-006', '2018-06-11T06:10:42+00:00', 'Zone - Area - Pohjois-Pasila'),
    ('XNJL-006', '2018-06-11T06:10:42+00:00', 'Zone - Area N Lauttasaari'),
    ('XNJL-006', '2018-06-11T06:10:42+00:00', 'Zone 2 Area H Taka-Töölö'),
    ('XNJL-006', '2019-07-03T11:50:51+00:00', 'Zone - Area - Denmark'),
    ('XNJL-006', '2019-07-03T11:50:51+00:00', 'Zone - Area - Pohjois-Pasila'),
    ('XNJL-006', '2019-07-03T11:50:51+00:00', 'Zone - Area N Lauttasaari'),
    ('XNJL-006', '2019-07-03T11:50:51+00:00', 'Zone 2 Area H Taka-Töölö'),
]

ALL_COMBINATIONS_REPEATS = 3
ALLOWED_COMBINATIONS_REPEATS = 50
PROCESS_COUNT = 8


def main(argv=sys.argv):
    verbose = ('-v' in argv[1:] or '--verbose' in argv[1:])
    set_authorization()
    measurements = measure_perfomance()
    results = process_measurements(measurements)

    print_results(results, verbose)


def set_authorization():
    global headers

    auth_token = get_auth_token()
    for header in list(headers):
        headers[header] = headers[header].format(auth_token=auth_token)


def get_auth_token():
    import django
    from django.contrib.auth import get_user_model

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkkihubi.settings')
    django.setup()

    first_admin_with_auth_token = (
        get_user_model().objects
        .filter(is_superuser=True)
        .exclude(auth_token=None)
        .first())

    if not first_admin_with_auth_token:
        raise SystemExit('No admin user with auth token found')

    return first_admin_with_auth_token.auth_token


def measure_perfomance():
    input_params_list = list(build_input_params())
    input_data_items = convert_params_to_post_data(input_params_list)

    with multiprocessing.Pool(processes=PROCESS_COUNT) as pool:
        (results, total_time) = execute_queries(pool, input_data_items)

    return (input_params_list, results, total_time)


def build_input_params():
    for reg_nr in registration_numbers:
        for (location, coords) in locations.items():
            for timestamp in timestamps:
                for _ in range(ALL_COMBINATIONS_REPEATS):
                    yield (timestamp, reg_nr, coords)

    for _ in range(ALLOWED_COMBINATIONS_REPEATS):
        for (reg_nr, timestamp, location) in expected_alloweds:
            coords = locations[location]
            yield (timestamp, reg_nr, coords)


def convert_params_to_post_data(input_params_list):
    return [
        build_post_data(*input_params)
        for input_params in input_params_list]


def build_post_data(timestamp, reg_nr, coords):
    post_params = {
        'time': timestamp,
        'registration_number': reg_nr,
        'location': {
            'longitude': coords[0],
            'latitude': coords[1],
        }
    }
    post_data = json.dumps(post_params, separators=(',', ':')).encode('utf-8')
    return post_data


def execute_queries(pool, input_data_items):
    results = []

    start_time = time.time()

    for post_data in input_data_items:
        results.append(pool.apply_async(measure_single, (post_data,)))

    for result in results:
        result.wait()

    end_time = time.time()

    return (results, end_time - start_time)


def process_measurements(measurements):
    (input_params_list, results, total_time) = measurements

    times = {}
    alloweds = []
    responses = {}
    fluctuating_responses = {}

    for (input_params, result) in zip(input_params_list, results):
        (timestamp, reg_nr, coords) = input_params
        location = location_by_coords[coords]
        params = (reg_nr, timestamp, location)

        (response, took) = result.get()

        response_data = {'status_code': response.status_code}
        try:
            response_data['data'] = response.json()
        except ValueError:
            pass

        times.setdefault(params, []).append(took)

        if response_data.get('data', {}).get('allowed'):
            if params not in alloweds:
                alloweds.append(params)

        last_response_data = responses.setdefault(params, response_data)

        if last_response_data != response_data:
            responses = fluctuating_responses.setdefault(
                params, [last_response_data])
            if response_data not in responses:
                responses.append(response_data)

    return {
        'times': times,
        'total_time': 1000.0 * total_time,
        'alloweds': alloweds,
        'responses': responses,
        'fluctuating_responses': fluctuating_responses,
    }


def measure_single(post_data):
    start_time = time.time()
    response = requests.post(url, headers=headers, data=post_data)
    end_time = time.time()
    took = 1000.0 * (end_time - start_time)
    return (response, took)


def print_results(results, verbose=False):
    all_times = sum((times for times in results['times'].values()), [])

    if verbose:
        print_responses(results)
        print()

    print_histogram(all_times)
    print()

    print_total_times(all_times, results)
    print()

    print_time_stat_figures(all_times)

    if verbose:
        print()
        print_alloweds(results)

    print_unexpected_alloweds(results)

    print_fluctuating_responses(results)


def print_responses(results):
    print('Responses:')
    for (params, response_data) in sorted(results['responses'].items()):
        data = response_data.get('data')
        status_code = response_data.get('status_code')
        allowed = (data and data.get('allowed'))
        print('{params:70} => {err:1}{code:3} {allowed:7} {data}'.format(
            params=' '.join(params),
            err='' if status_code == 200 else '*',
            code=status_code,
            allowed='ALLOWED' if allowed else '',
            data=json.dumps(data, sort_keys=True)))


def print_histogram(all_times):
    bins = [(x / 10.0, (x + 5) / 10.0) for x in range(155, 790, 5)]
    bins[0] = (0.0, bins[0][1])
    bins[-1] = (bins[-1][0], float('inf'))
    bin_counts = {
        (bin_min, bin_max): sum(1 for x in all_times if bin_min < x <= bin_max)
        for (bin_min, bin_max) in bins
    }
    max_count = max(bin_counts.values())
    line_count = 15
    scale = float(line_count) / max_count
    for level in range(line_count, 0, -1):
        print('|' + ''.join(
            '#' if bin_counts[bin_id] * scale >= level else ' '
            for bin_id in bins) + '|')
    print('+' + ''.join(
        '^' if bin_max % 10 == 0 else '-'
        for (bin_min, bin_max) in bins) + '+')
    print(' ' + ''.join(
        '{:3.0f}'.format(bin_max) if bin_max % 10 == 0 else
        '' if bin_max % 10 in [1, 2] else ' '
        for (bin_min, bin_max) in bins))


def print_total_times(all_times, results):
    print('Total combined waiting time: {:.3f} ms per {} requests'.format(
        sum(all_times), len(all_times)))
    print('Total {:.3f} ms real time per {} requests'.format(
        results['total_time'], len(all_times)))
    print((
        '\n'
        '  => {:7.3f} ms/req\n'
        '  => {:7.1f} reqs/s\n'
        '     **************').format(
            results['total_time'] / len(all_times),
            1000.0 * len(all_times) / results['total_time']))


def print_time_stat_figures(all_times):
    sorted_times = sorted(all_times)
    count = len(sorted_times)
    median = (
        sorted_times[count // 2] if count % 2 == 1 else
        (sorted_times[count // 2] + sorted_times[count // 2 + 1]) / 2.0)

    print('Minimum time: {:.3f} ms'.format(min(all_times)))
    print('Mean time:    {:.3f} ms'.format(sum(all_times) / len(all_times)))
    print('Median time:  {:.3f} ms'.format(median))
    print('Maximum time: {:.3f} ms'.format(max(all_times)))


def print_alloweds(results):
    print('Parking was allowed for following combinations:')
    for (reg_nr, timestamp, location) in results['alloweds']:
        print('  {:9} {} {}'.format(reg_nr, timestamp, location))


def print_unexpected_alloweds(results):
    extra_alloweds = set(results['alloweds']) - set(expected_alloweds)
    not_allowed_as_should = set(expected_alloweds) - set(results['alloweds'])
    if extra_alloweds:
        print()
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('Extra alloweds:\n{}'.format(
            '\n'.join(map(str, extra_alloweds))))
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    if not_allowed_as_should:
        print()
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('Not allowed as should:\n{}'.format(
            '\n'.join(map(str, not_allowed_as_should))))
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


def print_fluctuating_responses(results):
    fluctuating_responses = results['fluctuating_responses']
    if fluctuating_responses:
        print()
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print('Fluctuating responses:')
        for (params, responses) in fluctuating_responses.items():
            print('Params {}, responses:'.format(params))
            for response_data in responses:
                print('  - {}'.format(response_data))
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


if __name__ == '__main__':
    main()
