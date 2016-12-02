#!/usr/bin/env python
"""
Data model.
"""

from mongokit import Document
from importlib import import_module

to_register = []


def db_register(doc):
    if doc not in to_register:
        to_register.append(doc)


class BaseDocument(Document):
    __database__ = 'store'
    __collection__ = 'store'
    use_dot_notation = True


class AutorefsDocument(BaseDocument):
    user_autorefs = True


def init_db_docs(app):
    import_module('app.modules')
    for doc in to_register:
        print("Registering Document:", doc.__name__)
        app.db.register(doc)
