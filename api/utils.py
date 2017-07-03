"""
Utils
"""
import os
from threading import Thread
from flask import request
from flask_restful import Resource
from werkzeug.routing import BaseConverter, ValidationError
from bson.objectid import ObjectId
from bson.errors import InvalidId
import http

import easypost
easypost.api_key = os.environ['EASYPOST_API_KEY']

import stripe
stripe.api_key = os.environ['STRIPE_KEY']

from .database import Document

def make_json_response(status=200, message=None, data=None):
    resp = {}
    resp['status'] = http.HTTPStatus(status).phrase
    if message is not None:
        resp['message'] = message
    if data is not None:
        resp['data'] = data
    return resp, status

class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(value)
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        return str(value)

def to_json(res):
    if isinstance(res, Document):
        res = dict(res)
    elif isinstance(res, list):
        if len(res) == 0:
            res = []
        elif isinstance(res[0], Document):
            res = map(dict, res)
    return res


def default_dec(func):
    def wrapped(*args, **kwargs):
        res = func(*args, **kwargs)
        print('running')
        if isinstance(res, tuple):
            message, status = res
            data = None
            if isinstance(message, dict):
                data = message
                message = None
            if isinstance(data, dict) and \
               {'message', 'status', 'data'} > data.keys():
               return data, status
        else:
            message, status = None, 200
            data = to_json(res)
        return make_json_response(status, message, data)
    return wrapped


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
        view = default_dec(view)
        if decorators:
            for decorator in decorators:
                view = decorator(view)

        return view(*args, **kwargs)


def check_data(data, allowed=[], required=False):
    BAD_REQUEST = "There was an error processing the request. '{}' is invalid"
    BAD_REQUEST_REQUIRED = "There was an error processing the request. Required value '{}' is missing."
    BAD_REQUEST_CODE = 400

    for k in data:
        if k not in allowed:
            return False, (BAD_REQUEST.format(k), BAD_REQUEST_CODE)

    if required:
        for k in required:
            if k not in data:
                return False, (BAD_REQUEST_REQUIRED.format(k),
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
