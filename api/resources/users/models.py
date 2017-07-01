import os
from datetime import datetime
from passlib.hash import bcrypt
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from functools import wraps
from flask import request, make_response
from bson.objectid import ObjectId

from ...database import db, Document
from ..products.models import Product
from .package import package


def requires_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return "Access denied; no token", 401

        user = User.verify_auth_token(token)
        if not user or not user.exists:
            response = make_response("Token expired")
            response.status_code = 419
            response.set_cookie('token', '', expires=0)
            return response

        return func(user, *args, **kwargs)

    return check_token

def requires_admin():
    if request.method == 'OPTIONS':
        return

    token = request.cookies.get('token')
    if not token:
        return "Access denied; no token", 401

    user = User.verify_auth_token(token)
    if not user or not user.exists:
        response = make_response("Token expired")
        response.status_code = 419
        response.set_cookie('token', '', expires=0)
        return response

    if not user.admin:
        return "Access denied; not admin", 401


class User(Document):
    _collection = db.users
    _schema =  [
        # '_id', # Email
        'password',
        'first_name',
        'last_name',
        'contact_number',
        'create_time',
        'active',
        'cart', # {'product': 'amount'}
        'admin',
        'default_address',
    ]
    _check = [
        '_id',
        'first_name',
        'last_name'
    ]

    @staticmethod
    def _format_new(**kwargs):
        # TODO: Add email verification.

        kwargs['password'] = bcrypt.hash(kwargs['password'])
        kwargs['cart'] = {}

        if 'admin' not in kwargs:
            kwargs['admin'] = False

        return {
            **kwargs,
            'create_time': datetime.now(),
            'active': True
        }

    def check_password(self, password):
        return bcrypt.verify(password, self['password'])

    @classmethod
    def login(cls, email, password):
        user = cls(email)
        if user.exists and bcrypt.verify(password, user['password']):
            return True
        return False

    def generate_auth_token(self, expiration=60 * 60):
        s = Serializer(os.environ['FLASK_SECRET'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @classmethod
    def verify_auth_token(cls, token):
        s = Serializer(os.environ['FLASK_SECRET'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            # valid token, but expired
            return None
        except BadSignature:
            # invalid token
            return None
        user = cls(data['id'])
        return user

    def add_to_cart(self, item, amount=None):
        if amount is not None:
            self['cart'][item] = amount - 1

        if item not in self['cart']:
            self['cart'][item] = 0

        self['cart'][item] += 1

    def empty_cart(self):
        for item in list(self['cart']):
            del self['cart'][item]
        self.update()

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

    @property
    def cart_sums(self):
        cart = self['cart']
        measurements = []
        sub_total = 0

        for item, quantity in cart.items():
            item = Product(ObjectId(item))
            for _ in range(quantity):
                measurements.append(item._doc['measurements'])
            sub_total += item._doc['cost'] * quantity

        sizes = package(measurements)
        shipping_costs = [s.cost for s in sizes]

        return sub_total, [sum(c) for c in zip(*shipping_costs)]

    @property
    def admin(self):
        return self._doc['admin']


class Address(Document):
    _collection = db.addresses
    _schema = [
        'user',
        'name',
        'line1',
        'line2',
        'line3',
        'city',
        'county',
        'postcode'
    ]
    _check = [
        'name',
        'line1',
        'city',
        'county',
        'postcode'
    ]

    @staticmethod
    def _format_new(**kwargs):
        return kwargs
