from flask import request

from ..utils import check_data, Resource
from ..resources.products import (Products, Product, ProductImage,
                                  Categories, pass_product)
from ..resources.products import models


def valid_file(image):
    return image.content_type == 'image/jpeg'


class ProductsAdmin(Products):
    def get(self):
        return models.Product.find()

    def post(self):
        REQUIRED = [
            'desciption',
            'cost', 'name',
            'recipes', 'category_ids',
            'active'
        ]
        RECIPES_REQUIRED = [
            'name', 'url'
        ]
        data = request.get_json(force=True)

        # Check product data.
        allowed, resp = check_data(data, REQUIRED, True)
        if not allowed:
            return resp

        # Check recipe data.
        allowed, resp = check_data(data['recipes'],
                                   RECIPES_REQUIRED, True)
        if not allowed:
            return resp

        if 'category_ids' in data:
            category_ids = data['category_ids']
            del data['category_ids']

        product = models.product.new(**data)
        product.categories = category_ids
        return product


class ProductAdmin(Product):
    def get(self, product):
        return product

    def put(self, product):
        ALLOWED = [
            'description', 'cost',
            'name', 'recipes', 'category_ids',
            'active'
        ]
        RECIPES_REQUIRED = [
            'name', 'url'
        ]
        data = request.get_json(force=True)
        # Check product data.
        allowed, resp = check_data(data, ALLOWED)
        if not allowed:
            return resp

        # Check recipe data.
        if 'recipes' in data and len(data['recipes']):
            allowed, resp = check_data(data['recipes'],
                                       RECIPES_REQUIRED, True)
        if not allowed:
            return resp

        if 'category_ids' in data:
            product.categories = data['category_ids']
            del data['category_ids']

        if data:
            res = product.update(data)
            if not res['nModified']:
                return "SEVER ERROR; not modified.", 500

        return product


class ProductImageAdmin(Resource):
    decorators = [pass_product]

    def post(self, product, image_index):
        for file in request.files:
            if not valid_file(file):
                return 400
            product.add_image(file)

        return product

    def put(self, product, image_index):
        if image_index > len(product['images']):
            return "NOT FOUND; image does not exist", 404

        file = request.files['file']
        if not valid_file(file):
            return 400

        file = file.stream.read()
        if image_index == len(product['images']):
            image_index = None
        product.add_image(file, image_index)

        return product

    def delete(self, product, image_index):
        if image_index >= len(product['images']):
            return "NOT FOUND; image does not exist", 404

        del product['images'][image_index]
        product.update()


def register_resources(admin_api):
    admin_api.add_resource(ProductsAdmin, '/products')
    admin_api.add_resource(Categories, '/categories')

    admin_api.add_resource(ProductAdmin, '/products/<ObjectID:id>')
    admin_api.add_resource(
        ProductImageAdmin,
        '/products/<ObjectID:id>/<int:image_index>'
    )
