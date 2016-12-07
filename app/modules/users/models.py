from datetime import datetime
from passlib.hash import bcrypt

from flask_login import login_user

from ...database import db, Document

class User(Document):
    _collection = db.users
    _schema =  [
        '_id', # Email
        'password',
        'first_name',
        'last_name',
        'contact_num',
        'create_time',
        'active',
        {
            'default_addresses': [
                'billing',
                'shipping'
            ]
        }
    ]
    _check = [
        'first_name',
        'last_name'
    ]

    @staticmethod
    def _format_new(**kwargs):
        # TODO: Add verification.

        kwargs['password'] = bcrypt.hash(kwargs['password'])

        return {
            **kwargs,
            'create_time': datetime.now(),
            'active': True
        }

    @property
    def is_authenticated(self):
        return self.exists

    @property
    def is_active(self):
        return self.exists and self['active']

    @property
    def is_anonymous(self):
        return self.exists

    def get_id(self):
        return self._id

    @classmethod
    def login(cls, email, password):
        user = cls(email)
        if user.exists:
            if bcrypt.verify(password, user['password']):
                login_user(user)
            else:
                user = None
        return user


class Address(Document):
    _collection = db.addresses
    _schema = [
        'user',
        'full_name',
        'line1',
        'line2',
        'line3',
        'city',
        'county',
        'postcode'
    ]
    _check = [
        'full_name',
        'line1',
        'city',
        'county',
        'postcode'
    ]

    @staticmethod
    def _format_new(**kwargs):
        return kwargs

