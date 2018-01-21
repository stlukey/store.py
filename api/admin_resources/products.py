from flask import request
from bson.objectid import ObjectId

from ..utils import check_data, Resource
from ..resources.products import (Products, Product,
                                  Categories, pass_product)
from ..resources.products import models

ERROR_NOT_MODIFIED =\
"An error occurred. Product has not been modified. Please try again."
ERROR_INVALID_MESUREMENTS =\
"Invalid Mesurements. Please modify and try again."
ERROR_RELATED_PRODUCT_NOT_FOUND=\
"Related product not found."

RELATED_PRODUCT_ADDED =\
"Item added to related products."
RELATED_PRODUCT_REMOVED =\
"Item removed from related products."



class ProductsAdmin(Products):
    def get(self):
        products = list(models.Product.find(active=True))
        for i in range(len(products)):
            related = []            
            for related_id in products[i]['related'].keys():
                related_product = dict(models.Product(ObjectId(related_id)))
                del related_product['related']
                related.append(dict(related_product))
            products[i]['related'] = related

        return products

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
        related = []            
        for related_id in product['related'].keys():
            related_product = dict(models.Product(ObjectId(related_id)))
            del related_product['related']
            related.append(dict(related_product))

        product['related'] = related

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

class ProductsRelated(Resource):
    decorators = [pass_product]
    def put(self, product, related_id):
        if not models.Product(related_id).exists:
            return ERROR_RELATED_PRODUCT_NOT_FOUND, 404

        product['related'][str(related_id)] = True
        product.update()
        return RELATED_PRODUCT_ADDED, 200

    def delete(self, product, related_id):
        try:
            del product['related'][str(related_id)]
        except KeyError:
            return ERROR_RELATED_PRODUCT_NOT_FOUND, 400
        product.update()
        return RELATED_PRODUCT_REMOVED, 200
        

def register_resources(admin_api):
    admin_api.add_resource(ProductsAdmin, '/products')
    admin_api.add_resource(Categories, '/categories')

    admin_api.add_resource(ProductAdmin, '/products/<ObjectID:id>')
    admin_api.add_resource(ProductsRelated, '/products/<ObjectID:id>/related/<ObjectID:related_id>')
