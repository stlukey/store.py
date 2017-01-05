"""
Utils
"""
import os
from flask import request
from flask_restful import Resource
from werkzeug.routing import BaseConverter, ValidationError
from bson.objectid import ObjectId
from bson.errors import InvalidId

import easypost
easypost.api_key = os.environ['EASYPOST_API_KEY']

from .database import Document


class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(value)
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()

    def to_url(self, value):
        return str(value)


def default_dec(func):
    def wrapped(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, Document):
            res = dict(res)
        elif isinstance(res, list):
            if len(res) == 0:
                res = []
            elif isinstance(res[0], Document):
                res = map(dict, res)
        return res
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
    BAD_REQUEST = "BAD REQUEST; '{}' is invalid"
    BAD_REQUEST_REQUIRED = "BAD REQUEST; required value '{}' missing"
    BAD_REQUEST_CODE = 400

    for k in data:
        if k not in allowed:
            return False, (BAD_REQUEST.format(k), BAD_REQUEST_CODE)

    if required:
        for k in allowed:
            if k not in data:
                return False, (BAD_REQUEST_REQUIRED.format(k),
                               BAD_REQUEST_CODE)

    return True, None
