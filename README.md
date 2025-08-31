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

Workers can be scaled by calling `docker-compose up --scale celery_worker=<number>`.

### Celery Eventlet Configuration

The project now uses Eventlet for Celery worker concurrency, which can improve memory consumption and handle many concurrent I/O operations efficiently. Key settings:

- **Pool**: `eventlet` (configured in settings.py)
- **Default concurrency**: 1000 green threads
- **Memory management**: Workers restart after 1000 tasks or 200MB memory usage
- **Custom limits**: Set via `CELERY_MAX_TASKS_PER_CHILD` and `CELERY_MAX_MEMORY_PER_CHILD` environment variables

To monitor memory consumption, check worker logs or use system monitoring tools.

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

# Celery Worker Memory Management:
CELERY_MAX_TASKS_PER_CHILD=1000          # Tasks per worker before restart
CELERY_MAX_MEMORY_PER_CHILD=200000       # Memory limit in KB before restart

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
