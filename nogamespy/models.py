from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import ClauseElement

from .database import Base, db_session


# https://gist.github.com/codeb2cc/3302754
def get_or_create(_model, _session=db_session, _defaults={}, **kwargs):
    query = _session.query(_model).filter_by(**kwargs)

    instance = query.first()

    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items()
                      if not isinstance(v, ClauseElement))
        params.update(_defaults)
        instance = _model(**params)

        db_session.add(instance)
        # db_session.commit()  old DB schema forbids null values for some columns

        return instance, True


class Map(Base):
    __tablename__ = 'map'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    # TODO relations to modes & servers


class Mode(Base):
    __tablename__ = 'mode'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    # TODO relations to maps & servers


class MapMode(Base):
    __tablename__ = 'mapmode'

    id = Column(Integer, primary_key=True)

    map_id = Column(ForeignKey('map.id'), index=True)
    mode_id = Column(ForeignKey('mode.id'), index=True)

    map = relationship('Map')
    mode = relationship('Mode')


class Server(Base):
    __tablename__ = 'server'

    id = Column(Integer, primary_key=True)

    ip = Column(String)
    info_port = Column('infoport', Integer)
    port = Column(Integer)

    name = Column(String)
    map_id = Column(ForeignKey('map.id'), index=True)
    mode_id = Column(ForeignKey('mode.id'), index=True)

    country = Column(String)
    country_name = Column('countryname', String)

    version = Column(String)
    hradba = Column(String)
    num_players = Column('numplayers', Integer)
    max_players = Column('maxplayers', Integer)

    password = Column(Boolean)
    dedicated = Column('dedic', Boolean)
    vietnam = Column(Boolean)

    online = Column(Boolean)
    online_since = Column('onlineSince', DateTime, default=func.now())
    offline_since = Column('offlineSince', DateTime)

    map = relationship('Map')
    mode = relationship('Mode')
    players = relationship('Player', back_populates='server')
    # TODO cascade delete of players

    def __repr__(self):
        return f'<Server ip={self.ip} info_port={self.info_port} name={self.name}>'


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    ping = Column(Integer)
    frags = Column(Integer)

    server_id = Column(ForeignKey('server.id'), index=True)

    online = Column(Boolean, default=True)
    online_since = Column('onlineSince', DateTime, default=func.now())

    server = relationship('Server', back_populates='players')
