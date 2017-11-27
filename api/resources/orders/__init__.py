from flask import request

from .models import Order as OrderModel

from ...utils import Resource, check_data, stripe
from ..users.models import requires_token
from ..admin.models import Shipment

from ...emails import order_confirmation

import paypalrestsdk

paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": "AUDVe4PIXHRyGJTsEWce8taryZPazwPBST-K4025LYGOg52c50pDQZ5kl7YTRp1kATOVkzx026NOplF1",
    "client_secret": "EERmhFT8KJfz-I5xhWrNP0qZ5iUUtq7jbwT2lbMpkILSK3Zhda9C-X7XCPRvi2zaDayNKmX4CI0iB81X"
})


ERROR_CHARGE_CREATION =\
"""An error occured while creating the charge.
Please check your details."""
ERROR_ORDER_NOT_FOUND =\
"That order could not be found."
ERROR_ORDER_FORBIDDEN =\
"That order is not accessible to you."
ERROR_OUT_OF_STOCK =\
"""Insufficent stock to complete your order.
Your basket has been updated.
Please review and try again."""

ORDER_SUCCESSFUL =\
"Order placed successfully."

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
            'line3',
            'paypal'
        ]
        data = request.get_json(force=True)
        allowed, resp = check_data(data, ALLOWED, REQUIRED)
        if not allowed:
            return resp

        if not user.cart_in_stock:
            return ERROR_OUT_OF_STOCK, 503

        # Compute Total
        sub_total, shipping = user.cart_sums
        shipping = shipping[int(data['shipping_method'])]
        total = int(round(sub_total + shipping, 2) * 100)

        # Process payment
        try:
            if data['card_token']['type'] == "paypal":
                charge = paypalrestsdk.Payment.find(data['card_token']['data']['paymentID'])
                total_c = float(charge['transactions'][0]['amount']['total'])
                total_c = int(round(total_c, 2) * 100)

                if total != total_c:
                    raise Exception()

                if not charge.execute({'payer_id' : data['card_token']['data']['payerID']}):
                    raise Exception()


            else:
                charge = stripe.Charge.create(
                    amount=total,
                    currency="GBP",
                    source=data['card_token']   ['data'],
                    description="Charge for {} {} <{}>".format(
                        user['first_name'],
                        user['last_name'],
                        user.id
                    )
                )
        except Exception as e:
            return ERROR_CHARGE_CREATION, 400

        order_data = {
            'user': user,
            'items': user['cart'],
            'payment': {
                'amount': total,
                'id': charge['id'],
                'data': charge
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
        order_confirmation(user, order)

        user.empty_cart(update_stock=True)

        return (order, ORDER_SUCCESSFUL), 200

class Order(Resource):
    decorators = [requires_token]

    def get(self, user, _id):
        order = OrderModel(_id)
        if not order.exists:
            return ERROR_ORDER_NOT_FOUND, 404

        if not order.can_view(user):
            return ERROR_ORDER_FORBIDDEN, 403

        status = "pending"
        if ('shipment' in order._doc['shipping'] and
            order._doc['shipping']['shipment'] is not None):
            status = "processing"

            shipment = Shipment(order._doc['shipping']['shipment'])

            if ('dispatch_datetime' in shipment._doc and
                shipment._doc['dispatch_datetime'] is not None):
                status = "dispatched"

        return dict(status=status, **dict(order))

def register_resources(api):
    api.add_resource(Orders, '/orders')
    api.add_resource(Order, '/orders/<ObjectID:_id>')
