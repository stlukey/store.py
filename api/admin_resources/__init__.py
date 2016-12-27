from flask_restful import Api

from flask import make_response
from bson.json_util import dumps

from . import products
#from . import users
#from . import cart
#from . import pages


def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


def register_resources(admin):
    admin_api = Api(admin)
    admin_api.representations = {
        'application/json': output_json
    }

    products.register_resources(admin_api)
    #users.register_resources(admin_api)
    #cart.register_resources(admin_api)
    #pages.register_resources(admin_api)
