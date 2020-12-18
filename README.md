# Introduction

Sets the Nest home/away status according to the result of periodically checking a list of IPs.

If at least one host is connected to the local network, the status will be set to `home`.

If no hosts are connected, the status will be set to `away`.

# Setup

## Requirements

- [nest-rest](https://github.com/emilburzo/nest-rest) already setup and running
- static IPs set in your DHCP server (usually your router) for all the relevant phones

## Docker

The easiest way is to run it via Docker:

```bash
docker run -d \
--name nest-home-away \
  -e NEST_ACCESS_TOKEN="NEST_ACCESS_TOKEN" \
  -e NEST_STRUCTURE="NEST_STRUCTURE" \
  -e NEST_USER="NEST_USER" \
  -e NEST_REST_ENDPOINT="NEST_REST_ENDPOINT" \
  -e HOSTS="HOSTS" \
  -e TZ="TZ" \
  emilburzo/nest-home-away:latest
```

## Parameters

- `NEST_ACCESS_TOKEN`, `NEST_STRUCTURE` and `NEST_USER`:
  see [nest-rest documentation](https://github.com/emilburzo/nest-rest#nest-access-token-and-user-id)
- `NEST_REST_ENDPOINT`: the URL where [rest-nest](https://github.com/emilburzo/nest-rest) is running,
  e.g. `http://192.168.0.4:8467`
- `HOSTS`: usually static IPs of mobile devices that the script should check, e.g. `192.168.0.30,192.168.0.31`
- `TZ`: [timezone database name](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), if not set it will default to UTC; e.g. `Europe/Romania`
