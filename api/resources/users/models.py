import os
import datetime
from passlib.hash import bcrypt
from functools import wraps
from flask import request, current_app, request
from bson.objectid import ObjectId
import jwt

from ...database import db, Document
from ..products.models import Product
from .package import package

ERROR_LOGIN_REQUIRED = 'You must login to do that.'
ERROR_SESSION_EXPIRED = 'Session expired. Please login again.'
ERROR_NOT_ACTIVATED = 'Account not active. Please check your email.'
ERROR_NOT_ADMIN = "You must be an admin to do that!"

def requires_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):

        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ' '
        if not auth_token:
            return ERROR_LOGIN_REQUIRED, 401

        try:
            user = User.decode_auth_token(auth_token)
        except jwt.ExpiredSignatureError:
            return ERROR_SESSION_EXPIRED, 401
        except jwt.InvalidTokenError:
            return ERROR_SESSION_EXPIRED, 401

        if not user['active']:
            return ERROR_NOT_ACTIVATED, 401

        return func(user, *args, **kwargs)

    return check_token

def requires_admin():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ' '
    if not auth_token:
        return ERROR_LOGIN_REQUIRED, 401

    try:
        user = User.decode_auth_token(auth_token)
    except jwt.ExpiredSignatureError:
        return ERROR_SESSION_EXPIRED, 401
    except jwt.InvalidTokenError:
        return ERROR_SESSION_EXPIRED, 401

    if not user['admin']:
        return ERROR_NOT_ADMIN, 403




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

        kwargs['password'] = bcrypt.hash(kwargs['password'])
        kwargs['cart'] = {}

        if 'admin' not in kwargs:
            kwargs['admin'] = False

        if 'active' not in kwargs:
            kwargs['active'] = False

        return {
            **kwargs,
            'datetime': datetime.datetime.now()
        }

    def check_password(self, password):
        return bcrypt.verify(password, self['password'])

    @classmethod
    def login(cls, email, password):
        user = cls(email)
        if user.exists and user.check_password(password):
            return True
        return False

    def encode_auth_token(self):
        """
        Generates the Auth Token.
        :return: string
        """
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iat': datetime.datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @classmethod
    def decode_auth_token(cls, auth_token):
        """
        Decodes the auth token.
        :param auth_token:
        :return: integer|string
        :raises: ExpiredSignatureError, InvalidTokenError
        """
        payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
        user = cls(payload['sub'])
        if not user.exists:
            raise jwt.InvalidTokenError
        return user

    def add_to_cart(self, item, amount=None):
        if amount is not None:
            self['cart'][item] = amount - 1

        if item not in self['cart']:
            self['cart'][item] = 0

        self['cart'][item] += 1

    def empty_cart(self, update_stock=False):
        for item in list(self['cart']):
            if update_stock:
                p = Product(ObjectId(item))
                p['stock'] -= self['cart'][item]
                p.update()

            del self['cart'][item]

        self.update()


    def remove_inactive_items(self):
        cart = self['cart']
        for item in list(cart):
            p = Product(ObjectId(item))
            if not p['active']:
                del cart[item]

        self.update({'cart': cart})


    @property
    def cart_in_stock(self):
        avalible = True
        for item in list(self['cart']):
            p = Product(ObjectId(item))
            if p['stock'] < self['cart'][item]:
                if p['stock'] < 1:
                    del self['cart'][item]
                else:
                    self['cart'][item] = p['stock']
                avalible = False
        self.update()
        return avalible

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
