#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import timeit

import requests

url = 'http://127.0.0.1:8000/enforcement/v1/check_parking/'

headers = {
    'Content-type': 'application/json',
    'Authorization': 'ApiKey a4ac1cf9313ad0e72c99a9960102fdc81dbce2c5'
}

registration_numbers = (
    "LUÅ-972",  # valid
    "NYP-917",
    "OBX-712",
    "MCM-271",
    "ABC-123",
    "XX-456",
    "MCM271"  # valid
)

locations = (
    (24.919685, 60.184667),  # inside Paymentzone 2
    (24.9603955, 60.1805608),  # inside Paymentzone 1
    (24.862739, 60.149293),  # inside Parking-zone N
    (24.927108, 60.217988),  # outside Parking-zone or Permit-area
    (12.354040, 56.007643),  # Outside Finland
    (24.9205277, 60.1666692)
)


timestamps = (
    '2018-06-26 10:17:50+00:00',  # valid timestamp
    '2018-06-11 06:10:42+00:00',
    '2019-06-11 06:10:42+00:00',
    '2018-08-05 01:55:11+00:00'  # valid timestamp
)


def measure_perfomance():
    start_time = timeit.default_timer()
    for reg_nr in registration_numbers:
        for location in locations:
            for timestamp in timestamps:
                post_data = {
                    'time': timestamp,
                    'registration_number': reg_nr,
                    'location':
                    {
                        'longitude': location[0],
                        'latitude': location[1]
                    }
                }
                requests.post(url, headers=headers, data=json.dumps(post_data))

    print('Took {} seconds '.format(timeit.default_timer() - start_time))


if __name__ == '__main__':
    measure_perfomance()
