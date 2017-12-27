from factory import lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory
from faker import Factory

from nogamespy import models
from nogamespy.database import db_session


lazy = lambda call: lazy_attribute(lambda obj: call())

faker = Factory.create()


class Map(SQLAlchemyModelFactory):

    class Meta:
        model = models.Map
        sqlalchemy_session = db_session

    name = lazy(faker.word)


class Mode(SQLAlchemyModelFactory):

    class Meta:
        model = models.Mode
        sqlalchemy_session = db_session

    name = lazy(faker.word)


class Server(SQLAlchemyModelFactory):

    class Meta:
        model = models.Server
        sqlalchemy_session = db_session

    name = lazy(faker.word)


class Player(SQLAlchemyModelFactory):

    class Meta:
        model = models.Player
        sqlalchemy_session = db_session

    name = lazy(faker.word)
