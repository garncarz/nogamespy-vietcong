# NoGameSpy-Vietcong

[![Build Status](https://travis-ci.org/garncarz/nogamespy-vietcong.svg?branch=master)](https://travis-ci.org/garncarz/nogamespy-vietcong)
[![Coverage Status](https://coveralls.io/repos/github/garncarz/nogamespy-vietcong/badge.svg?branch=master)](https://coveralls.io/github/garncarz/nogamespy-vietcong?branch=master)

Crawls servers hosting multi-player game and saves information via ORM into DB.
Acts as an alternative master server.


## Usage

Needed: Docker

If you want to overwrite settings or persist a SQLite database (but PostgreSQL/MySQL can be used as well),
create your local volume directory (`$VOLUME`).
The application will use `db.sqlite` and `settings_local.py` from this location.

Ports used are:
- 28900 TCP for the master server (game clients fetching the server list)
- 27900 UDP for the heartbeat service (game servers introducing themselves)

DB schema migration:
`docker run -it -v $VOLUME:/app/volume garncarz/nogamespy-vietcong alembic upgrade head`
(needs to be run before the first use and on every change of the schema)

Master server:
`docker run -it -v $VOLUME:/app/volume -p 28900:28900 garncarz/nogamespy-vietcong ./app.py --master`

Heartbeat service:
`docker run -it -v $VOLUME:/app/volume -p 27900:27900/udp garncarz/nogamespy-vietcong ./app.py --heartbeat`

Pull new servers from Qtracker:
`docker run -it -v $VOLUME:/app/volume garncarz/nogamespy-vietcong ./app.py --new`

Refresh servers (players, maps, etc.):
`docker run -it -v $VOLUME:/app/volume garncarz/nogamespy-vietcong ./app.py --refresh`


## Development

Needed: Python 3, Docker

Optionally: PostgreSQL or MySQL

`pip install -r requirements.txt`

`./setup.py build`

`alembic upgrade head` (needs to be rerun every time a DB migration is released)

`PYTHONPATH=build/lib.linux-x86_64-3.6 ./app.py --help`
(the exact `lib*` subdirectory name depends on the version of Python)

`alembic revision [--autogenerate] -m "<migration message>"` (creates a new DB migration)

`./test.sh` (runs tests and also generates a coverage)

`docker build -t nogamespy-vietcong .`

`docker run -it nogamespy-vietcong bash`

`docker run -it -v <local volume path>:/app/volume nogamespy-vietcong ./app.py --help`
