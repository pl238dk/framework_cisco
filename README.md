# Cisco API Framework

This is a framework that connects to the API of Cisco's main feature collection.

## Authentication

Credentials are stored in JSON format, in the same directory as the `cisco.py` file. The name of the file should be `credentials.json`.

Other authentication methods, such as KDBX, have been tested, but this way it keeps the hard-coded passwords out of the source code.

```
{
    "servers": {
        "feature_name": {
            "client_id": "",
            "client_secret": ""
        }
    }
}
```

As features are requested through Cisco's website, a pair of `client_id` and `client_secret` values are provided to authenticate.

The first feature granted is the `hello` API endpoint, which simply tests whether or not the credentials are successful.

## Getting Started

To instantiate a `Cisco` object, pass a string of the credential name created in the "Authentication" section :

```
>>> feature_name = 'hello'
>>> c = Cisco(config=feature_name)
```

To test the `hello` endpoint, initiate a `get_request` passing the URI path as follows :

```
>>> r = c.get_request('hello')
```

## API Console Features

As of the most recent update, grabbing EoX data is the only feature currently explored.

Three functions exist :
- Grab EoX data by passing a product name.
- Grab EoX data by passing a serial number.
- Grab EoX data by passing a start-date and end-date when an EoX event might exist.

To grab an EoX range :

```
>>> date_start = '2000-01-01'
>>> date_end = '2040-12-31'

>>> data = c.get_eox_date_range(date_start, date_end)
>>> c.store_data(data['result'])
```

To convert the JSON data into a Python dictionary format :

```
>>> data_dict = c.json_to_dict(data['result'])
```