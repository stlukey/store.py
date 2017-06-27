#!/usr/bin/env python3
"""
Minimal ORM for Mongodb

:author: Luke Southam <luke@devthe.com>
"""


from pymongo import MongoClient
import os

client = MongoClient(os.environ.get('MONGODB_URI', 'localhost'))
db = client[os.environ.get('MONGODB_NAME', 'online-store')]

class ValidationError(Exception):
    @classmethod
    def not_provided(cls, key):
        return cls("'{}' not provided.".format(key))


def make_spec(schema, **kwargs):
    """
    Generate spec from schema and values.

    :param schema: list of spec keys
    :param kwargs: spec keys and values
    :return: spec dict
    """
    # A _id value must be given if in schema.
    if '_id' in schema and kwargs.get('_id') is None:
        raise ValidationError.not_provided('_id')

    spec = dict()
    for k in schema:
        # Support for embedded documents.
        if isinstance(k, dict):
            for embedded, fields in k.items():
                if kwargs.get(embedded) is not None:
                    spec[embedded] = make_spec(fields, **kwargs[embedded])

        # Only add item if a value is given.
        elif kwargs.get(k) is not None:
            spec[k] = kwargs[k]

    # Allow lookup by ObjectID
    if '_id' in kwargs:
        spec['_id'] = kwargs['_id']

    return spec


class Document(object):
    """
    Mongodb document management.

    Inherit from this and set:
        _collection: The mongodb collection (from pymongo)
        _schema: The collection schema (list of fields)
        _check: List of fields that must have values when inserted.
        _format_new: ran on spec before a new document is inserted (staticmethod)
    """

    # spec = make_spec
    spec = classmethod(lambda cls, **kwargs: make_spec(cls._schema, **kwargs))
    _check = []

    @classmethod
    def new(cls, **kwargs):
        """ 
        Insert new document.

        :param kwargs: values
        :return: Document instance
        """
        try:
            kwargs = cls._format_new(**kwargs)
        except KeyError as e:
            raise ValidationError.not_provided(e.args[0])

        for field in cls._check:
            if field not in kwargs:
                raise ValidationError.not_provided(field)

        spec = cls.spec(**kwargs)

        _id = cls._collection.insert(spec)
        return cls(_id)

    @staticmethod
    def _format_new(**kwargs):
        return kwargs

    def __init__(self, _id=None, _doc=None, **kwargs):
        if _doc is not None:
            self._doc = _doc
            return

        if _id is not None:
            kwargs['_id'] = _id

        spec = self.spec(**kwargs)
        self._doc = self._collection.find_one(spec)

    @classmethod
    def find(cls, _sort=False, **kwargs):
        spec = cls.spec(**kwargs)
        docs = cls._collection.find(spec)
        if _sort:
            docs = docs.sort(*_sort)

        return [cls(doc['_id']) for doc in docs]

    @classmethod
    def find_one(cls, **kwargs):
        spec = cls.spec(**kwargs)
        doc = cls._collection.find_one(spec)
        return cls(doc)

    def __getitem__(self, item):
        return self._doc[item]

    @property
    def id(self):
        return self._doc['_id']

    def update(self, _set=None, _inc=None):
        if _set is None and _inc is None:
            _set = self._doc

        update = {}
        if _set is not None:
            update['$set'] = _set
        if _inc is not None:
            update['$inc'] = _inc

        res = self._collection.update(
            {'_id': self.id},
            update
        )
        self._doc = self.__class__(self.id)._doc
        return res

    @property
    def exists(self):
        return self._doc is not None

    def delete(self):
        self._collection.delete_one({'_id': self.id})
        self._doc = None

    def __iter__(self):
        for k, v in self._doc.items():
            yield k, v
