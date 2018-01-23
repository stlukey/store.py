"""
Utils
"""
import os
from threading import Thread
from flask import request, make_response
from flask_restful import Resource
from werkzeug.routing import BaseConverter, ValidationError
from bson.objectid import ObjectId
from bson.errors import InvalidId
from bson.json_util import dumps
from http import HTTPStatus

import easypost
easypost.api_key = os.environ['EASYPOST_API_KEY']

import stripe
stripe.api_key = os.environ['STRIPE_KEY']

from .database import Document

class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(value)
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        return str(value)

dict_no_none = lambda d: dict((k, v) for k, v in d.items() if v is not None)

class JSONResponse(object):
    __dict__ = lambda self: dict_no_none({
        'status': HTTPStatus(self.status).phrase,
        'message': self.message,
        'data': self.data
    })

    dump = lambda self: dumps(self.__dict__())

    def __init__(self, message=None, data=None, status=200):
        self.status = status
        self.message = message
        self._data = data

    @property
    def data(self):
        data = self._data
        # MongoDB Doc
        if isinstance(data, Document):
            data = dict(data)
        # List of MongoDB Doc
        elif isinstance(data, list):
            if len(data) == 0:
                data = []
            elif isinstance(data[0], Document) or hasattr(data[0], '_id'):
                data = map(dict, data)
        return data

    @classmethod
    def make_response(cls, payload, status=200):
        # payload = JSONResponse(....)
        if isinstance(payload, cls):
            obj = payload

        # payload = message
        elif isinstance(payload, str):
            obj = cls(payload, None, status)

        # payload = (data, message)
        elif isinstance(payload, tuple) and len(payload) == 2:
            data, message = payload
            obj = cls(message, data, status)

        # payload = data
        else:
            obj = cls(None, payload, status)

        return make_response(obj.dump(), status)


def output_json(data, status=200, headers=None):
    resp = JSONResponse.make_response(data, status)
    resp.headers.extend(headers)
    return resp


class Resource(Resource):
    _decorators = {}

    def dispatch_request(self, *args, **kwargs):
        """Derived MethodView dispatch to allow for decorators to be
            applied to specific individual request methods - in addition
            to the standard decorator assignment.

            Example decorator use:
            decorators = [user_required] # applies to all methods
            _decorators = {
                'post': [admin_required, format_results]
            }
        """

        view = super(Resource, self).dispatch_request
        decorators = self._decorators.get(request.method.lower())
        if decorators:
            for decorator in decorators:
                view = decorator(view)

        return view(*args, **kwargs)


def fix_id(k):
    if k == '_id':
        return 'email'
    return k

def check_data(data, allowed=[], required=False):
    BAD_REQUEST = "There was an error processing the request.\n'{}' is invalid"
    BAD_REQUEST_REQUIRED = "There was an error processing the request.\nRequired value '{}' is missing."
    BAD_REQUEST_CODE = 400

    for k in data:
        if k not in allowed:
            return False, (BAD_REQUEST.format(fix_id(k)), BAD_REQUEST_CODE)

    if required:
        for k in required:
            if k not in data:
                return False, (BAD_REQUEST_REQUIRED.format(fix_id(k)),
                               BAD_REQUEST_CODE)

    return True, None

def in_context(f):
    from . import app
    def wrapper(*args, **kwargs):
        with app.app_context():
            return f(*args, **kwargs)
    return wrapper

def async(f):
    f = in_context(f)
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
