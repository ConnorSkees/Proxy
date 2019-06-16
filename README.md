# Proxy
A module and CLI for quickly finding and testing proxies

## Requirements
Python 3.6+

## Usage 
### Positional Arguments
* `count` The number of proxies.
### Optional Arguments
* `-ex --exclude [EX...]` Types of proxies to exclude. Valid values include country codes (US, CA, etc.), country names (United States, Canada, etc.), and proxy anonymity levels (elite proxy, anonymous, and transparent)
* `-r --require [R...]` Include only proxies with these attributes. Valid values include country codes (US, CA, etc.), country names (United States, Canada, etc.), and proxy anonymity levels (elite proxy, anonymous, and transparent)
* `--validate` Validate the proxies against a random website to make sure they work.
* `--http-only` Only get http proxies
* `--https-only` Only get https proxies
* `-v --verbose` Get full data on proxy (country code, country name, and anonymity level)

## Examples
Get one random proxy:

`python proxy 1`

Get 5 random http proxies from the United States

`python proxy 5 --http-only --require us`

Get 300 random proxies not from Russia

`python proxy 300 --exclude russian federation`

Import proxy to use in your own code
```
import requests
from proxy import proxy
requests.get('http://github.com', proxies={'http':proxy(1, require=['united states', 'ca'], validate=False)})
```
