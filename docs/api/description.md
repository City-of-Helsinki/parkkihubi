# Parkkihubi REST APIs

  **NOTE!** The public API is on very initial state. Backward
  incompatible changes are possible.

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
