from flask import request
from ..utils import Resource, check_data
from ..resources.admin import models
from ..resources.orders.models import Order
from datetime import datetime


class Shipments(Resource):
    def get(self):
        return models.Shipment.find()

    def post(self):
        """
        Put all pending orders in shipment.
        """
        current = models.Shipment(dispatch_datetime={'$exists': False})
        if current.exists:
            return "BAD REQUEST; Shipment pending.", 400
        
        current = models.Shipment.new()

        orders_pending = Order.find({'shipping': {'shipment': {'$exists': False}}})
        for order in orders_pending:
            shipping = order['shipping']
            shipping['shipment'] = current.id
            order.update(_set={'shipping': shipping})

        return current

    def put(self):
        """
        Mark shipment as shipped.
        """
        current = models.Shipment(dispatch_datetime={'$exists': False})
        if not current.exists:
            return "BAD REQUEST; No shipment pending.", 400

        current.update(_set=dict(dispatch_datetime=datetime.now()))
        return current

class Shipment(Resource):
    def get(self, _id):
        shipment = models.Shipment(_id)
        if not shipment.exists:
            return "NOT FOUND", 404

        orders = Order.find({'shipping': {'shipment': shipment.id}})

        return dict(orders=orders, **dict(shipment))


def register_resources(admin_api):
    admin_api.add_resource(Shipments, '/shipments')
    admin_api.add_resource(Shipment, '/shipments/<ObjectID:_id>')
