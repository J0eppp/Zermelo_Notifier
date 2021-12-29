import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relation, relationship, sessionmaker

import os

from zermelo import Client

database_uri = os.getenv("DATABASE_URI")
engine = sa.create_engine(database_uri)
SQLAlchemyBase = declarative_base()
Session = sessionmaker(bind=engine)


class User(SQLAlchemyBase):
    __tablename__ = "user"
    id = sa.Column(sa.Integer, primary_key=True)
    discord_id = sa.Column(sa.String(512), nullable=False)
    date_registered = sa.Column(sa.DateTime, nullable=False)
    zermelo_schoolname = sa.Column(sa.String(64), nullable=False)
    zermelo_access_token = sa.Column(sa.String(256), nullable=False)

    def get_client(self) -> Client:
        return Client(self.zermelo_schoolname)

    @staticmethod
    def get_user_by_discord_id(session, discord_id) -> "User":
        return session.query(User).filter(User.discord_id == discord_id).first()


SQLAlchemyBase.metadata.create_all(engine)


def insert(session, obj, commit=True):
    """Insert object into the database"""
    if obj:
        session.add(obj)
    if commit == True:
        session.commit()


def merge(session, obj, commit=True):
    """Merge object into the database"""
    if obj:
        session.merge(obj)
    if commit == True:
        session.commit()


def delete(session, obj, commit=True):
    """Delete object from the database"""
    if obj:
        session.delete(obj)
    if commit == True:
        session.commit()
