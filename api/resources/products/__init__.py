from flask import send_file, redirect
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
    def get(self, product, image_index):
        print(image_index, range(len(product['images'])), product['images'])
        if image_index not in range(len(product['images'])):
            return redirect('https://placehold.it/410x308')
            #return 'NOT FOUND', 404
        return send_file(product.get_image(image_index))


class Products(Resource):
    def get(self):
        return models.Product.find(active=True)


class ProductsLatest(Resource):
    def get(self):
        return [
            product for product in
                models.Product.find(_sort=("datetime", 1))
        ][:3]


class ProductsPopular(Resource):
    def get(self):
        return [
            product for product in models.Product.find()
                if 'popular' in [product.id for product in
                                    product.categories]
        ]


class Category(Resource):
    def get(self, id):
        category = models.Category(id)
        if not category.exists:
            return "NOT FOUND", 404
        return category.products


class Categories(Resource):
    def get(self):
        return {cat.id:cat.name for cat in models.Category.find()}


def register_resources(api):
    api.add_resource(Products, '/products/')
    api.add_resource(ProductsLatest, '/products/latest')
    api.add_resource(ProductsPopular, '/products/popular')

    api.add_resource(Product, '/products/<ObjectID:id>')
    api.add_resource(ProductImage, '/products/<ObjectID:id>/<int:image_index>.jpg')

    api.add_resource(Categories, '/categories/')
    api.add_resource(Category, '/categories/<string:id>')

