from flask import request

from .models import Order as OrderModel

from ...utils import Resource, check_data, stripe
from ..users.models import requires_token


class Orders(Resource):
    decorators = [requires_token]

    def get(self, user):
        return OrderModel.find(user=user.id)

    def post(self, user):
        REQUIRED = [
            'name',
            'line1',
            'city',
            'county',
            'postcode',
            'card_token',
            'shipping_method'
        ]
        ALLOWED = REQUIRED + [
            'line2',
            'line3'
        ]
        data = request.get_json(force=True)
        allowed, resp = check_data(data, ALLOWED, REQUIRED)
        if not allowed:
            return resp

        # TODO: Check and update stock

        # Compute Total
        sub_total, shipping = user.cart_sums
        shipping = shipping[int(data['shipping_method'])]
        total = int(round(sub_total + shipping, 2) * 100)

        # Process payment
        try:
            charge = stripe.Charge.create(
                amount=total,
                currency="GBP",
                source=data['card_token'],
                description="Charge for {} {} <{}>".format(
                    user['first_name'],
                    user['last_name'],
                    user.id
                )
            )
        except Exception as e:
            return "PAYMENT ERROR; {}".format(e), 400


        order_data = {
            'user': user,
            'items': user['cart'],
            'payment': {
                'amount': total,
                'id': charge['id']
            },
            'shipping': {
                'address': {
                    'name': data['name'],
                    'line1': data['line1'],
                    'line2': data.get('line2'),
                    'line3': data.get('line3'),
                    'city': data['city'],
                    'county': data['county'],
                    'postcode': data['postcode']
                },
                'method': data['shipping_method'],
                'shipment': None
            }
        }

        order = OrderModel.new(**order_data)

        user.empty_cart()

        return order

class Order(Resource):
    decorators = [requires_token]

    def get(self, user, _id):
        order = OrderModel(_id)
        if not order.exists:
            return "NOT FOUND", 404

        if not order.can_view(user):
            return "FORBIDDEN", 403

        return order


def register_resources(api):
    api.add_resource(Orders, '/orders')
    api.add_resource(Order, '/orders/<ObjectID:_id>')
