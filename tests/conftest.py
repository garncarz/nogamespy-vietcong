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
    with database.db_engine.connect() as conn:
        conn.execute(database.sqlalchemy.text('drop schema if exists public cascade'))
        conn.execute(database.sqlalchemy.text('create schema public'))
        conn.commit()
    models.Base.metadata.create_all(database.db_engine)

    yield

    database.db_session.close_all()
    with database.db_engine.connect() as conn:
        conn.execute(database.sqlalchemy.text('drop schema public cascade'))
        conn.commit()
