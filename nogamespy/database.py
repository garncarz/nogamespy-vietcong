from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import settings

engine = create_engine(
    settings.DATABASE,
    convert_unicode=True,
)

db_session = scoped_session(
    sessionmaker(autocommit=False,
                 autoflush=False,
                 bind=engine),
)

Base = declarative_base()
Base.query = db_session.query_property()
