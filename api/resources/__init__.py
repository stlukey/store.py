from flask_restful import Api

from flask import make_response
from bson.json_util import dumps

from . import products
from . import users
from . import cart
from . import pages
from . import orders


def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


def register_resources(app):
    api = Api(app)
    api.representations = {
        'application/json': output_json
    }

    products.register_resources(api)
    users.register_resources(api)
    cart.register_resources(api)
    pages.register_resources(api)
    orders.register_resources(api)
