# -*- coding: utf-8 -*-

from cromlech.sqlalchemy import create_engine, SQLAlchemySession
from uvclight import IRootObject
from zope.interface import implementer
from zope.location import Location

from .admin import get_valid_messages, Admin, styles


@implementer(IRootObject)
class LoginRoot(Location):

    def __init__(self, pkey, dest, dburl, dbkey):
        self.pkey = pkey
        self.dest = dest
        self.dbkey = dbkey
        self.engine = create_engine(dburl, dbkey)
        self.engine.bind(Admin)

    def get_base_messages(self):
        messages = []
        with SQLAlchemySession(self.engine) as session:
            messages = get_valid_messages(session)
        return messages

    def get_messages(self):
        return [{'msg': m.message, 'type': m.type, 'style': styles[m.type]}
                for m in self.get_base_messages()]
