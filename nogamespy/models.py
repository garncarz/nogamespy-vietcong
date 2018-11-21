from datetime import datetime, timedelta
import logging

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func, or_, inspect
from sqlalchemy.orm import relationship
from sqlalchemy.sql import ClauseElement

from .database import Base, db_session
from . import settings

logger = logging.getLogger(__name__)


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


def delete_if_persistent(instance):
    if inspect(instance).persistent:
        db_session.delete(instance)
        return True

    return False


class Map(Base):
    __tablename__ = 'map'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    modes = relationship('Mode', secondary='mapmode')
    servers = relationship('Server')

    def __repr__(self):
        return f'<Map name={self.name}>'


class Mode(Base):
    __tablename__ = 'mode'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    maps = relationship('Map', secondary='mapmode')
    servers = relationship('Server')

    def __repr__(self):
        return f'<Mode name={self.name}>'


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
    waiting_for_sync = Column(Boolean, default=False)

    map = relationship('Map', back_populates='servers')
    mode = relationship('Mode', back_populates='servers')
    players = relationship('Player', back_populates='server')

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

    def __repr__(self):
        return f'<Player name={self.name} server={self.server.name}>'


def remove_offline_entities():
    players_deleted = Player.query.filter(
        or_(
            Player.online == False,
            Player.server.has(Server.online == False),
        ),
    ).delete(synchronize_session='fetch')

    Server.query.filter(
        Server.online == True,
        Server.offline_since is not None,
    ).update({
        'offline_since': None,
    })

    servers_went_offline = Server.query.filter(
        Server.online == False,
        Server.offline_since.is_(None),
    ).update({
        'offline_since': datetime.now(),
    }, synchronize_session='fetch')

    servers_deleted = Server.query.filter(
        Server.online == False,
        Server.offline_since < datetime.now() - timedelta(minutes=settings.KEEP_OFFLINE_SERVERS_FOR_MINUTES),
    ).delete()

    db_session.commit()

    if players_deleted:
        logger.debug(f'{players_deleted} offline players deleted.')

    if servers_went_offline:
        logger.debug(f'{servers_went_offline} servers went offline.')

    if servers_deleted:
        logger.info(f'{servers_deleted} offline servers deleted.')
