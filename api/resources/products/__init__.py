from ...utils import Resource
from . import models
from bson.objectid import ObjectId
from flask_restful import Resource as Resource_
from bson.objectid import ObjectId

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
    
        related = []            
        for related_id in product['related'].keys():
            related_product = dict(models.Product(ObjectId(related_id)))
            del related_product['related']
            if related_product['active']:
                related.append(dict(related_product))
        product['related'] = related

        return product


class Products(Resource):
    def get(self):
        products = list(models.Product.find(active=True))
        for i in range(len(products)):
            related = []            
            for related_id in products[i]['related'].keys():
                related_product = dict(models.Product(ObjectId(related_id)))
                del related_product['related']
                if related_product['active']:
                    related.append(dict(related_product))
            products[i]['related'] = related

        return products


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
                if 'customer-favourites' in [cat.id for cat in
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


    api.add_resource(Categories, '/categories')
    api.add_resource(Category, '/categories/<string:id>')
