# Parkkihubi REST APIs

## Different APIs

Parkkihubi has four different REST APIs:

* [Operator API](../operator/)

  Operator API can be used to manage parking events and parking permits.
  The API is designed to be used by parking operators and other parking
  service providers.

* [Enforcement API](../enforcement/)

  Enforcement API can be used to check validity of parkings in relation
  to the operator created parking events and parking permits.  The API
  is designed to be used by a system which serves the parking
  enforcement personnel.

* [Public API](../public/)

  Public API can be used to get some statistics about the parking areas.
  The API is designed to be available for anyone.

  **NOTE!** The public API is on very initial state. Backward
  incompatible changes are possible.

* Monitoring API

  Monitoring API can be used to monitor the status of the Parkkihubi.
  The API is designed to be used by the Parkkihubi Dashboard.

## Object Model

### Parking (Event)

Parking is a parking event created by a parking operator.  It has a
start time and an end time.  The parking can be either paid or free
(e.g. a parking disc parking).  Parkkihubi doesn't handle or record
parking payments at the moment.

Parkings record an actual parking event that is happening in the real
world (or has happened when looking back in time for statistics). They
are usually created in real time when the parking event starts.  The end
time is usually updated when the parking event ends. (Parkings cannot be
created postactively after the parking event has started, because the
parking enforcement personnel wouldn't be able to check them in real
time.)

### Parking Permit

Parking Permit is a permit created by a parking operator.  It has a list
of subjects (i.e. registration numbers) and a list of permitted areas.
Each assigned subject and area in the permit has a separate validity
period.  A parking is valid by the permit when the registration number
and the area match and their corresponding validity periods cover the
parking time.

Parking permits should be created in advance, before the parking events
start.  They are also used to check if a parking event is valid or not,
but with the permits the actual parking times are not recorded.  Parking
permits are usually created for a longer period of time (e.g. a month or
a year).

### Permit Series

Permits are grouped into permit series.  Permit series ara used as a
mechanism to allow activating and deactivating permits in bulk.

## Method Override

Parkkihubi REST APIs support using the Method Override.

### What Is Method Override?

Method Override is a way to override the HTTP method of a request. This
is useful when you want to perform an action of a different HTTP method
than the one the client is using, e.g. when you want to perform a
`PATCH` request but the client only supports `GET` and `POST`.

### How To Use the Method Override in Parkkihubi

Parkkihubi supports using a `method` query parameter for overriding the
HTTP method of a request.  For example, if you want to perform a `PATCH`
request, you can send a `POST` request with a `method=PATCH` query
parameter.

#### Example

Here is an example of how to use the Method Override to update a parking
end time, which would normally be done with a `PATCH` request, but is
here done with a `POST` request instead.

```bash
ID=abcd1234-1234-1234-1234-123456789012  # A parking ID

curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"time_end": "2023-10-20T17:00:00+0300"}' \
  "https://testapi.parkkiopas.fi/operator/v1/parking/$ID/?method=PATCH"
```

For comparison here is how it would look like without the Method
Override:

```bash
curl -X PATCH \
  -H "Content-Type: application/json" \
  -d '{"time_end": "2023-10-20T17:00:00+0300"}' \
  "https://testapi.parkkiopas.fi/operator/v1/parking/$ID/"
```

### Limitations

The Method Override is only supported when the carrying request is using
`POST` method and `application/json` content type.  It can only be used
to override the method to `PATCH`, `PUT` or `DELETE`.

It is not possible to override the method to `GET` or `POST`, since
these are assumed to be universally supported by clients.
