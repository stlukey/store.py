from datetime import datetime
from passlib.hash import bcrypt

from flask_httpauth import HTTPBasicAuth

from ...database import db, Document

auth = HTTPBasicAuth()

class User(Document):
    _collection = db.users
    _schema =  [
        '_id', # Email
        'password',
        'first_name',
        'last_name',
        'contact_number',
        'create_time',
        'active',
        'cart', # {'product': 'amount'}
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
        # TODO: Add email verification.

        kwargs['password'] = bcrypt.hash(kwargs['password'])
        kwargs['cart'] = {}

        return {
            **kwargs,
            'create_time': datetime.now(),
            'active': True
        }

    @classmethod
    def login(cls, email, password):
        user = cls(email)
        if user.exists and bcrypt.verify(password, user['password']):
            return True
        return False

    def add_to_cart(item, amount=None):
        if amount is not None:
            self['cart'][item] = amount -1

        if item not in self['cart']:
            self['cart'][item] = 0

        self['cart'][item] += 1

    def update(self, set_=None, *args, **kwargs):
        format_cart = lambda cart: {
            str(item):amount for item, amount in cart.items()
                if amount > 0
        }
        if set_ is not None and 'cart' in set_:
            set_['cart'] = format_cart(set_['cart'])
        else:
            self._doc['cart'] = format_cart(self['cart'])

        return super(User, self).update(set_, *args, **kwargs)

    def __iter__(self):
        EXCLUDE = ['password']
        for k, v in super(User, self).__iter__():
            if k not in EXCLUDE:
                yield k, v




auth.verify_password(lambda email, pwd: User.login(email, pwd))

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

