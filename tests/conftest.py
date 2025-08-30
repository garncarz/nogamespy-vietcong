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
    # For SQLite, we just create all tables, no schema commands needed
    models.Base.metadata.create_all(database.db_engine)

    yield

    database.db_session.close_all()
    models.Base.metadata.drop_all(database.db_engine)
