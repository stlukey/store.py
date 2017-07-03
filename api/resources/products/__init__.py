from flask import send_file, redirect
from ...utils import Resource
from . import models
from bson.objectid import ObjectId
from flask_restful import Resource as Resource_

ERROR_PRODUCT_NOT_FOUND =  "That product can not be found."
ERROR_CATEGORY_NOT_FOUND = "That category can not be found."


def pass_product(func):
    def wrapped(id, *args, **kwargs):
        product = models.Product(id)
        if not product.exists:
            return ERROR_PRODUCT_NOT_FOUND, 404

        return func(product, *args, **kwargs)
    return wrapped


class Product(Resource):
    decorators = [pass_product]
    def get(self, product):
        if not product['active']:
            return ERROR_PRODUCT_NOT_FOUND, 404
        return product


class ProductImage(Resource_):
    def get(self, id):
        if id == 'placeholder':
            return redirect('https://placehold.it/410x308')

        id = ObjectId(id)
        image = models.get_image(id)
        return send_file(image, mimetype='image/jpeg')


class Products(Resource):
    def get(self):
        return models.Product.find(active=True)


class ProductsLatest(Resource):
    def get(self):
        return [
            product for product in
                models.Product.find(active=True, _sort=("datetime", -1))
        ][:3]


class ProductsPopular(Resource):
    def get(self):
        return [
            product for product in models.Product.find(active=True)
                if 'popular' in [product.id for product in
                                    product.categories]
        ]


class Category(Resource):
    def get(self, id):
        category = models.Category(id)
        if not category.exists:
            return ERROR_CATEGORY_NOT_FOUND, 404
        return category.products


class Categories(Resource):
    def get(self):
        return {cat.id:cat.name for cat in models.Category.find()
                # Only display categiories which have products.
                if len(models.ProductToCategory.find(category=cat.id))}


def register_resources(api):
    api.add_resource(Products, '/products')
    api.add_resource(ProductsLatest, '/products/latest')
    api.add_resource(ProductsPopular, '/products/popular')

    api.add_resource(Product, '/products/<ObjectID:id>')
    api.add_resource(ProductImage, '/images/<id>.jpg')


    api.add_resource(Categories, '/categories')
    api.add_resource(Category, '/categories/<string:id>')
