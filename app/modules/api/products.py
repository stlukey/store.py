from flask import current_app
from flask_restful import Resource
from ..products import queries


class Product(Resource):
    def get(self, id):
        return queries.product_get(id)

class Products(Resource):
    def get(self):
        return current_app.db.Product.find()


class Category(Resource):
    def get(self, name):
        return queries.product_find_by_category_or_abort(name)


class Categories(Resource):
    def get(self):
        return [cat[0] for cat in queries.categories_get_all()]

