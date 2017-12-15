from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base


class Map(Base):
    __tablename__ = 'maps'

    name = Column(String, primary_key=True)


class Mode(Base):
    __tablename__ = 'modes'

    name = Column(String, primary_key=True)


class MapMode(Base):
    __tablename__ = 'map_modes'

    id = Column(Integer, primary_key=True)

    map = Column(String, ForeignKey('maps.name'))
    mode = Column(String, ForeignKey('modes.name'))


class Server(Base):
    __tablename__ = 'servers'

    id = Column(Integer, primary_key=True)

    ip = Column(String)
    info_port = Column(Integer)
    port = Column(Integer)

    name = Column(String)
    map = Column(String, ForeignKey('maps.name'))
    mode = Column(String, ForeignKey('modes.name'))

    country = Column(String)
    country_name = Column(String)

    version = Column(String)
    hradba = Column(String)
    num_players = Column(Integer)
    max_players = Column(Integer)

    password = Column(Boolean)
    dedicated = Column(Boolean)
    vietnam = Column(Boolean)

    online = Column(Boolean)
    online_since = Column(DateTime, default=func.now())
    offline_since = Column(DateTime)

    players = relationship('Player', back_populates='server')


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)

    name = Column(String)
    ping = Column(Integer)
    frags = Column(Integer)

    server_id = Column(Integer, ForeignKey('servers.id'))

    online = Column(Boolean, default=True)
    online_since = Column(DateTime, default=func.now())

    server = relationship('Server', back_populates='players')
