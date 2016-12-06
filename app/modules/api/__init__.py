from flask import Blueprint
from flask_restful import Api

from flask import make_response
from bson.json_util import dumps

from .products import Product, Products, Category, Categories



def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp


api_bp = Blueprint('api', __name__)
api = Api(api_bp)
api.representations =  {'application/json': output_json}

api.add_resource(Products, '/products/')
api.add_resource(Product, '/products/<ObjectID:id>')
api.add_resource(Categories, '/products/categories/')
api.add_resource(Category, '/products/categories/<string:name>')



