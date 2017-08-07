from flask import request
from bson.objectid import ObjectId

from ...utils import Resource, check_data
from ..users.models import *
from ..products import pass_product
from ..products.models import Product

ERROR_NOT_MODIFIED =\
"""An error occurred.
Cart has not been modified.
Please try again."""


class Cart(Resource):
    decorators = [requires_token]

    def get(self, user):
        return user['cart']

    def delete(self, user):
        res = user.update({'cart': {}})
        if not res['nModified']:
            return ERROR_NOT_MODIFIED, 500
        return {}


class CartItem(Resource):
    decorators = Cart.decorators + [pass_product]

    def post(self, user, product):
        cart = user['cart']
        quantity = cart.get(str(product.id), 0) + 1
        cart[str(product.id)] = quantity

        res = user.update({'cart': cart})
        if not res['nModified']:
            return ERROR_NOT_MODIFIED, 500

        return cart

    def put(self, user, product):
        ALLOWED = ['quantity']
        data = request.get_json(force=True)

        allowed, resp = check_data(data, ALLOWED)
        if not allowed:
            return resp

        cart = user['cart']
        quantity = data.get('quantity', cart.get(str(product.id), 0))
        cart[str(product.id)] = quantity

        res = user.update({'cart': cart})
        if not res['nModified']:
            return ERROR_NOT_MODIFIED, 500

        return cart

    def delete(self, user, product):
        cart = user['cart']
        if str(product.id) in cart:
            del cart[str(product.id)]

        res = user.update({'cart': cart})
        if not res['nModified']:
            return ERROR_NOT_MODIFIED, 500

        return cart


class CartCost(Resource):
    decorators = Cart.decorators

    def get(self, user):
        sub_total, shipping = user.cart_sums
        return {
            'sub_total': sub_total,
            'shipping': shipping
        }


def register_resources(api):
    api.add_resource(Cart, '/cart')
    api.add_resource(CartItem, '/cart/<ObjectID:id>')
    api.add_resource(CartCost, '/cart/cost')
