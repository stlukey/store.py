from flask import request

from ..utils import check_data, Resource
from ..resources.products import (Products, Product,
                                  Categories, pass_product)
from ..resources.products import models

ERROR_NOT_MODIFIED =\
"An error occurred. Product has not been modified. Please try again."
ERROR_INVALID_MESUREMENTS =\
"Invalid Mesurements. Please modify and try again."


class ProductsAdmin(Products):
    def get(self):
        return models.Product.find()

    def post(self):
        REQUIRED = [
            'description',
            'cost', 'name',

            'width', 'depth',
            'length', 'weight'
        ]
        data = request.get_json(force=True)

        # Check product data.
        allowed, resp = check_data(data, REQUIRED, REQUIRED)
        if not allowed:
            return resp

        data['recipes'] = []
        data['stock'] = 0
        data['active'] = False

        data['measurements'] = {
            'width': float(data['width']),
            'depth': float(data['depth']),
            'length': float(data['length']),
            'weight': float(data['weight']),
        }
        del data['width']
        del data['depth']
        del data['length']
        del data['weight']

        data['cost'] = float(data['cost'])

        product = models.Product.new(**data)
        return product


class ProductAdmin(Product):
    def get(self, product):
        return product

    def put(self, product):
        ALLOWED = [
            'description', 'cost',
            'name', 'recipes', 'category_ids',
            'active', 'stock', 'images'

            'width', 'depth',
            'length', 'weight'

            '$inc'
        ]
        RECIPE_REQUIRED = [
            'name', 'url'
        ]
        data = request.get_json(force=True)
        # Check product data.
        allowed, resp = check_data(data, ALLOWED)
        # TODO: check why check_data does not accept weight.
        #if not allowed:
        #    return resp

        # Check recipe data.
        if 'recipes' in data and len(data['recipes']):
            for recipe in data['recipes']:
                allowed, resp = check_data(recipe,
                                           RECIPE_REQUIRED, RECIPE_REQUIRED)
                if not allowed:
                    return resp

        if 'category_ids' in data:
            product.categories = data['category_ids']
            del data['category_ids']

        if 'stock' in data:
            data['stock'] = int(data['stock'])

        try:
            measurements = {}
            for measurement in ['width', 'depth', 'length', 'weight']:
                if measurement in data and data[measurement]:
                    measurements[measurement] = float(data[measurement])
                    del data[measurement]
                elif measurement in product['measurements']:
                    measurements[measurement] = product['measurements'][measurement]
            if measurements != {}:
                data['measurements'] = measurements
        except ValueError:
            return 400, ERROR_INVALID_MESUREMENTS


        kwargs = {}
        if '$inc' in data and data['$inc']:
            del data['$inc']
            kwargs['_inc'] = data
        else:
            kwargs['_set'] = data

        if data:
            res = product.update(**kwargs)
            if not res['nModified']:
                return ERROR_NOT_MODIFIED, 500

        return product



def register_resources(admin_api):
    admin_api.add_resource(ProductsAdmin, '/products')
    admin_api.add_resource(Categories, '/categories')

    admin_api.add_resource(ProductAdmin, '/products/<ObjectID:id>')
