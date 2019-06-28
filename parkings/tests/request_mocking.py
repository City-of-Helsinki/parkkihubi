import os
from contextlib import contextmanager

import requests_mock

mydir = os.path.dirname(__file__)

URL_TO_RESPONSE_FILE_MAP = {
    ('https://kartta.hel.fi/ws/geoserver/avoindata/wfs'
     '?service=WFS&version=2.0.0&request=GetCapabilities'): (
         'wfs_capabilities_response.xml'),

    ('https://kartta.hel.fi/ws/geoserver/avoindata/wfs'
     '?service=WFS&version=2.0.0&request=GetFeature'
     '&typenames=avoindata%3Aliikennemerkkipilotti_pysakointipaikat'): (
         'parking_area_importer_data.xml'),

    ('https://kartta.hel.fi/ws/geoserver/avoindata/wfs'
     '?service=WFS&version=2.0.0&request=GetFeature'
     '&typenames=Asukas_ja_yrityspysakointivyohykkeet_alue'): (
         'permit_area_importer_data.xml'),

    ('https://kartta.hel.fi/ws/geoserver/avoindata/wfs'
     '?service=WFS&version=2.0.0&request=GetFeature'
     '&typenames=Pysakoinnin_maksuvyohykkeet_alue'): (
        'payment_zone_importer_data.xml'),
}


@contextmanager
def mocked_requests():
    with requests_mock.Mocker(real_http=False) as requests_mocker:
        for (url, response_file) in URL_TO_RESPONSE_FILE_MAP.items():
            with open(os.path.join(mydir, response_file), 'rb') as fp:
                response_content = fp.read()
            requests_mocker.get(url, content=response_content)

        yield requests_mocker
