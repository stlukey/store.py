from flask import request

from ...utils import Resource
from ..users.models import *
from ..users import pass_user
from ..products import pass_product

class Cart(Resource):
    decorators = [auth.login_required, pass_user]

    def get(self, user):
        return user['cart']

    def delete(self, user):
        res = user.update({'cart': {}})
        if not res['nModified']:
            return "SERVER ERROR; not modified.", 500
        return {}

class CartItem(Resource):
    decorators = Cart.decorators + [pass_product]

    def get(self, user, product):
        return user['cart'].get(str(product.id), 0)

    def post(self, user, product):
        cart = user['cart']
        amount = cart.get(str(product.id), 0) + 1
        cart[str(product.id)] = amount

        res = user.update({'cart': cart})
        if not res['nModified']:
            return "SERVER ERROR; not modified.", 500
        
        return cart.get(str(product.id), 0)

    def put(self, user, product):
        ALLOWED = ['amount']
        data = request.get_json(force=True)
        for k in data.keys():
            if k not in ALLOWED:
                return "BAD REQUEST; '{}' not allowed".format(k), 400
        
        cart = user['cart']
        amount = data.get('amount', cart.get(str(product.id), 0))
        cart[str(product.id)] = amount

        res = user.update({'cart': cart})
        if not res['nModified']:
            return "SERVER ERROR; not modified.", 500
        
        return cart.get(str(product.id), 0)

    def delete(self, user, product):
        cart = user['cart']
        if product.id in cart:
            del cart[str(product.id)]

        res = user.update({'cart': cart})
        if not res['nModified']:
            return "SERVER ERROR; not modified.", 500
        
        return cart.get(str(product.id), 0)

def register_resources(api):
    api.add_resource(Cart, '/cart')
    api.add_resource(CartItem, '/cart/<ObjectID:id>')

