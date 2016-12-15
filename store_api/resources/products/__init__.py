from flask import send_file
from ...utils import Resource
from . import models

def pass_product(func):
    def wrapped(id, *args, **kwargs):
        product = models.Product(id)
        if not product.exists:
            return "NOT FOUND", 404

        return func(product, *args, **kwargs)
    return wrapped

class Product(Resource):
    decorators = [pass_product]
    def get(self, product):
        return product


class ProductImage(Product):
    def get(self, product, name):
        if name not in product['images'].keys():
            return 'NOT FOUND', 404
        return send_file(product.get_image(name))


class Products(Resource):
    def get(self):
        return models.Product.find()


class Category(Resource):
    def get(self, id):
        category = models.Category(id)
        if not category.exists:
            return "NOT FOUND", 404
        return category.products


class Categories(Resource):
    def get(self):
        return [cat.id for cat in models.Category.find()]


def register_resources(api):
    api.add_resource(Products, '/products/')
    api.add_resource(Product, '/products/<ObjectID:id>')
    api.add_resource(ProductImage, '/products/<ObjectID:id>/<string:name>.jpg')

    api.add_resource(Categories, '/categories/')
    api.add_resource(Category, '/categories/<string:id>')

