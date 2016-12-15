"""
Utils
"""
from flask import request
from flask_restful import Resource
from werkzeug.routing import BaseConverter, ValidationError
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .database import Document

class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(value)
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        return str(value)

def std_dec(func):
    def wrapped(*args, **kwargs):
        res = func(*args, **kwargs)
        if isinstance(res, Document):
            res = dict(res)
        elif isinstance(res, list) and isinstance(res[0], Document):
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
        view = std_dec(view)
        if decorators:
            for decorator in decorators:
                view = decorator(view)

        return view(*args, **kwargs)

