from flask import Blueprint
from flask_restful import Api

from flask import make_response
from bson.json_util import dumps

from . import products
from . import users
from . import cart


def output_json(obj, code, headers=None):
    output = {
        "data": obj,
        "status": code
    }
    resp = make_response(dumps(output), code)
    resp.headers.extend(headers or {})
    return resp


def register_resources(app):
    api = Api(app)
    api.representations =  {
            'application/json': output_json
    }

    products.register_resources(api)
    users.register_resources(api)
    cart.register_resources(api)


