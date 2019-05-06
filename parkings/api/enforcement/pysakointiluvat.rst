Pysäköintilupien rajapinta
==========================

Rajapinta toimii kahden objektityypin kanssa:

 * Permit: Pysäköintilupa

 * PermitSeries: Pysäköintilupien sarja.  Mahdollistaa kaikkien lupien
   päivittämisen kerralla ilman katkoksia tietojen oikeellisuudessa.

Pysäköintiluvilla on seuraavat ominaisuudet:

 * "id": Luvan Parkkihubin tunniste

 * "external_id": Luvan ulkoinen tunniste (PASIn ID), jota voi käyttää
   esim. yksittäisen luvan päivittämiseen tai poistamiseen

 * "series": lupasarjan tunniste (int)

 * "start_time": luvan alkamisaika (ISO8601 muotoinen aikaleima)

 * "end_time": luvan loppumisaika (ISO8601 muotoinen aikaleima)

 * "subjects": luvan kohteena olevien autojen rekisterinumerot (lista
   stringejä)

 * "areas": luvan alueiden tunnukset (lista stringejä)


A. Kaikkien pysäköintilupien öinen päivitys
-------------------------------------------

 1. Luodaan uusi lupasarja (PermitSeries -objekti)

 2. Viedään kaikki pysäköintiluvat liittettynä tuohon juuri luotuun
    lupasarjaan.

 3. Aktivoidaan uusi lupasarja, jolloin edellinen lupasarja
    deaktivoituu.

A.1. Lupasarjan luominen
~~~~~~~~~~~~~~~~~~~~~~~~

Lupasarja luodaan lähetettämällä tyhjä POST-kutsu
permitseries-endpointtiin ja poimimalla talteen vastauksesta lupasarjan
tunniste ("id").

* Endpoint: enforcement/v1/permitseries/

* Metodi: POST

* Pyynnön muoto::

    {}

* Vastauksen muoto::

    {
      "id": 6,
      "created_at": "2019-05-05T23:45:05.587894Z",
      "modified_at": "2019-05-05T23:45:05.587964Z",
      "active": false
    }


A.2. Pysäköintilupien vieminen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pysäköintiluvat lisätään lupasarjaan lähettämällä ne POST-requesteilla
permit-endpointtiin.  Yhdessä POST-requestissa voi lähettää joko yhden
objektin kerrallaan tai useita objekteja (lupia) kerrallaan käyttämällä
lista-tyyppistä JSON-arvoa.

HUOM! "external_id"-kentän arvojen pitää olla uniikkeja sarjan sisällä,
eli saman sarjan kahdella eri luvalla ei saa olla samaa external_id:tä.

* Endpoint: enforcement/v1/permit/

* Metodi: POST

* Pyynnön muoto::

    [
      {
        "series": 6,
        "external_id": "10011",
        "start_time": "2019-04-27T12:00:00+03:00",
        "end_time": "2019-12-27T12:00:00+02:00",
        "subjects": ["ABC-123", "XYZ-456"],
        "areas": ["C", "D", "M"]
      },
      {
        "series": 6,
        "external_id": "10012",
        "start_time": "2019-04-28T12:00:00+03:00",
        "end_time": "2019-11-28T12:00:00+02:00",
        "subjects": ["ABC-124"],
        "areas": ["A", "D"]
      },
      {
        "series": 6,
        "external_id": "10013",
        "start_time": "2019-05-30T12:00:00+03:00",
        "end_time": "2020-01-30T12:00:00+02:00",
        "subjects": ["ABC-125"],
        "areas": ["E", "D"]
      },
      {
        "series": 6,
        "external_id": "10014",
        "start_time": "2019-06-27T12:00:00+03:00",
        "end_time": "2019-07-01T10:45:12+02:00",
        "subjects": ["ABC-126"],
        "areas": ["M"]
      }
    ]

  tai::

    {
      "series": 6,
      "external_id": "10011",
      "start_time": "2019-04-27T12:00:00+03:00",
      "end_time": "2019-12-27T12:00:00+02:00",
      "subjects": ["ABC-123", "XYZ-456"],
      "areas": ["C", "D", "M"]
    }

* Vastauksen muoto:

  Jos pyyntö on lista, niin palautetaan lista::

    [
      ...,
      {
        "id": 36022,
        "series": 6,
        "external_id": "10013",
        "start_time": "2019-05-30T09:00:00Z",
        "end_time": "2020-01-30T10:00:00Z",
        "subjects": ["ABC-125"],
        "areas": ["D", "E"]
      },
      ...
    ]

  tai, jos pyyntö on yksittäinen objekti, niin vastauskin on.

A.3. Lupasarjan aktivointi
~~~~~~~~~~~~~~~~~~~~~~~~~~

Lupasarja aktivoidaan lähettämällä tyhjä POST-kutsu
permitseries-activate -endpointtiin.  Tämä asettaa annetun lupasarjan
aktiiviseksi ja poistaa samalla aktiivisuuden muilta lupasarjoilta.
Parkkihubi tekee pysäköintilupien tarkistuksen vain aktiivisen
lupasarjan perusteella.

Huomaa, että allaolevassa endpointin osoitteessa {id} korvataan
lupasarjan tunnisteella, jolloin koko osoite on esim.
https://testapi.parkkiopas.fi/enforcement/v1/permitseries/6/activate/

* Endpoint: enforcement/v1/permitseries/{id}/activate/

* Metodi: POST

* Pyynnön muoto::

    {}

* Vastauksen muoto::

    {
      "status": "OK"
    }


B. Lupien päivittäminen kesken päivän
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aktiivisen lupasarjan lupia voi muuttaa luvan id:n tai external_id:n
perusteella.  Tiedot voi joko kokonaan korvata uusilla (metodi = PUT)
tai muuttaa yksittäisiä kenttiä (metodi = PATCH) tai poistaa koko luvan
(metodi = DELETE).

* Endpoint:
   - enforcement/v1/permit/{id}/  tai
   - enforcement/v1/active_permit_by_external_id/{external_id}/

* Metodi: PUT, PATCH tai DELETE

* Pyynnön muoto:

  PUT-pyynnössä pitää antaa koko objekti, esim.::

    {
      "series": 6,
      "external_id": "10013",
      "start_time": "2019-05-30T09:00:00Z",
      "end_time": "2020-03-31T23:59:00+03:00",
      "subjects": ["ABC-125"],
      "areas": ["D", "E", "F"]
    }

  PATCH-pyynnössä voidaan antaa vain muutettavat kentät, esim.::

    {
      "end_time": "2020-03-31T23:59:00+03:00",
      "areas": ["D", "E", "F"]
    }

  DELETE-pyynnössä ei tarvitse antaa pyynnölle sisältöä.

* Vastauksen muoto:

  PUT- ja PATCH-pyynnön vastauksena lähetetään päivitetty objekti, esim.::

    {
      "id": 36022,
      "series": 6,
      "external_id": "10013",
      "start_time": "2019-05-30T09:00:00Z",
      "end_time": "2020-03-31T20:59:00Z",
      "subjects": ["ABC-125"],
      "areas": ["D", "E", "F"]
    }

  Onnistuneen DELETE-pyynnön vastauksessa ei ole sisältöä vaan
  onnistumisen näkee status-koodista 204 onnistuneelle deletelle tai
  epäonnistuessa esim. 404, jos objektia ei löydy.
