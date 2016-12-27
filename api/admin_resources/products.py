from flask import request

from ..utils import check_data
from ..resources.products import Products, Product, ProductImage
from ..resources.products import models


def valid_file(image):
    return True


class ProductsAdmin(Products):
    def post(self):
        REQUIRED = [
            'desciption',
            'cost', 'name',
            'recipes'
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

        user = models.product.new(**data)
        return user


class ProductAdmin(Product):
    def put(self, product):
        ALLOWED = [
            'desciption', 'cost',
            'name', 'recipes'
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

        res = product.update(data)
        if not res['nModified']:
            return "SEVER ERROR; not modified.", 500
        return product


class ProductImageAdmin(ProductImage):
    def post(self, product):
        for file in request.files:
            if not valid_file(file):
                return 400
            product.add_image(file)

        return product['images']

    def put(self, product, image_index):
        if image_index >= len(product['images']):
            return "NOT FOUND; image does not exist", 404

        file = request.files['file']
        if not valid_file(400):
            return 400

        product._doc['images'][image_index] = file
        product.update()

        return product['images']

    def delete(self, product, image_index):
        if image_index >= len(product['images']):
            return "NOT FOUND; image does not exist", 404

        del product['images'][image_index]
        product.update()


def register_resources(admin_api):
    admin_api.add_resource(ProductsAdmin, '/products')

    admin_api.add_resource(Product, '/products/<ObjectID:id>')
    admin_api.add_resource(
        ProductImage,
        '/products/<ObjectID:id>/<int:image_index>.jpg'
    )
