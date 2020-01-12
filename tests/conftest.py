from nogamespy import settings

settings.DATABASE = 'postgresql://postgres@db/postgres'

try:
    from conftest_local import *
except ImportError:
    pass

import pytest

from nogamespy import database, models


@pytest.fixture(scope='module', autouse=True)
def db_create():
    database.db_engine.execute('drop schema if exists public cascade')
    database.db_engine.execute('create schema public')
    models.Base.metadata.create_all(database.db_engine)

    yield

    database.db_session.close_all()
    database.db_engine.execute('drop schema public cascade')
