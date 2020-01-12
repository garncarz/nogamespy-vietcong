# NoGameSpy-Vietcong

[![Build Status](https://travis-ci.org/garncarz/nogamespy-vietcong.svg?branch=master)](https://travis-ci.org/garncarz/nogamespy-vietcong)
[![Coverage Status](https://coveralls.io/repos/github/garncarz/nogamespy-vietcong/badge.svg?branch=master)](https://coveralls.io/github/garncarz/nogamespy-vietcong?branch=master)
[![Docker image](https://images.microbadger.com/badges/image/garncarz/nogamespy-vietcong.svg)](https://microbadger.com/images/garncarz/nogamespy-vietcong)

Crawls servers hosting multi-player game and saves information via ORM into DB.
Acts as an alternative master server.


## Usage

Needed: Docker, Docker Compose

You also need to have the `docker-compose.yml` file from this repository locally.

Run `docker-compose run master alembic upgrade head` to upgrade the DB schema.
It needs to be run before the first use and on every change of the schema.

Run `docker-compose up` to start all services. `Ctrl+C` to exit.

If you want them demonized, use `docker-compose up -d` and `docker-compose down`.

Published ports are:
- 28900 TCP for the master server (game clients fetch the servers list here)
- 27900 UDP for the heartbeat service (game servers introduce themselves here)


### Configuration

Optionally, use these environment variables (they can be in the `.env` file):

```py
# PostgreSQL:
DATABASE='postgresql://<user>:<password>@<host>[:<port>]/<dbname>[?<options>]'

# MySQL:
DATABASE='mysql+pymysql://<user>:<password>@<host>[:<port>]/<dbname>[?<options>]'

# Logging aggregation:
SENTRY_DSN='https://<token>@sentry.io/<project>'

# Counting statistics:
STATSD_HOST='...'
STATSD_PORT=8125
```


## Development

`./dev.sh build master`

`./dev.sh run master ./test.sh`

`./dev.sh run master ./app.py --help`

Under `./dev.sh run master bash`:

`alembic revision [--autogenerate] -m "<migration message>"` (creates a new DB migration)

`alembic upgrade head` (needs to be rerun every time a DB migration is released)


<!-- ❄️ Hello to the GitHub Archive! ❄️ -->
