# NoGameSpy-Vietcong

[![Build Status](https://travis-ci.org/garncarz/nogamespy-vietcong.svg?branch=master)](https://travis-ci.org/garncarz/nogamespy-vietcong)
[![Coverage Status](https://coveralls.io/repos/github/garncarz/nogamespy-vietcong/badge.svg?branch=master)](https://coveralls.io/github/garncarz/nogamespy-vietcong?branch=master)

Crawls servers hosting multi-player game and saves information via ORM into DB.
Acts as an alternate master server.


## Installation

Needed: Python 3

`pip install -r requirements.txt`

`./setup.py build`


## Usage

`PYTHONPATH=build/lib.linux-x86_64-3.6 ./app.py --help`
(the exact `lib*` subdirectory name depends on the version of Python)


## Development

`./test.sh` (runs tests and also generates a coverage)
