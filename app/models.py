#!/usr/bin/env python
"""
Data model.
"""

from mongokit import Document
from importlib import import_module

conns = []


class PartialConnection(object):
    def __init__(self):
        conns.append(self)
        self.documents = []

    def register(self, doc):
        self.documents.append(doc)
        return doc

    def complete(self, connection):
        for doc in self.documents:
            print("Registering Document:", doc.__name__)
            connection.register(doc)


class BaseDocument(Document):
    __database__ = 'heroku_8b9x3jg8'
    __collection__ = 'store'
    use_dot_notation = True


class AutorefsDocument(BaseDocument):
    user_autorefs = True


def init_db_docs(app):
    import_module('app.modules')
    for conn in conns:
        conn.complete(app.db)
