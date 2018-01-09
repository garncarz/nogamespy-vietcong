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
It will create a SQLite DB in `volume/db.sqlite` by default, but you can use PostgreSQL/MySQL if you want to.

Run `docker-compose up` to start all services. `Ctrl+C` to exit.

If you want them demonized, use `docker-compose up -d` and `docker-compose down`.

There will be a `volume` directory created (if it already does not exist).
It can contain `db.sqlite` and `settings_local.py` (overwritten settings) and the services will use them.

Published ports are:
- 28900 TCP for the master server (game clients fetch the servers list here)
- 27900 UDP for the heartbeat service (game servers introduce themselves here)


### Configuration

Optionally, `settings_local.py` can contain:

```py
# PostgreSQL:
DATABASE = 'postgresql://<user>:<password>@<host>[:<port>]/<dbname>[?<options>]'

# MySQL:
DATABASE = 'mysql+pymysql://<user>:<password>@<host>[:<port>]/<dbname>[?<options>]'

# Logging aggregation:
SENTRY_DSN = 'https://<key>:<secret>@sentry.io/<project>'

# Counting statistics:
STATSD_HOST = '...'
```

You can pass those values also in form of environment variables.


## Development

Needed extra: Python 3

`pip install -r requirements.txt -r requirements-test.txt`

`./setup.py build`

`alembic upgrade head` (needs to be rerun every time a DB migration is released)

`PYTHONPATH=build/lib.linux-x86_64-3.6 ./app.py --help`
(the exact `lib*` subdirectory name depends on the version of Python)

`alembic revision [--autogenerate] -m "<migration message>"` (creates a new DB migration)

`./test.sh` (runs tests and also generates a coverage)

`docker build -t nogamespy-vietcong -f Dockerfile-dev .`

`docker run -it nogamespy-vietcong bash`

`docker run -it -v <local volume path>:/app/volume nogamespy-vietcong ./app.py --help`
