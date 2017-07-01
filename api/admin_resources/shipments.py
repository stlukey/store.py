from flask import request
from ..utils import Resource, check_data
from ..resources.admin import models
from ..resources.orders.models import Order


class Shipments(Resource):
    def get(self):
        return models.Shipment.find()

    def post(self):
        """
        Put all pending orders in shipment.
        """
        current = models.Shipment.get_current()
        if current.exists:
            return "BAD REQUEST; Shipment pending.", 400


        orders_pending = Order.find_({'shipping.shipment': {'$exists': False}})
        if len(orders_pending) == 0:
            return "BAD REQUEST; No orders awaiting shipment.", 400

        current = models.Shipment.new()

        for order in orders_pending:
            order.update({'shipping.shipment': current.id})

        return current

    def put(self):
        """
        Mark shipment as shipped.
        """
        current = models.Shipment.get_current()
        if not current.exists:
            return "BAD REQUEST; No shipment pending.", 400

        current.mark_as_dispatched()

        return current

class Shipment(Resource):
    def get(self, _id):
        shipment = models.Shipment(_id)
        if not shipment.exists:
            return "NOT FOUND", 404

        orders = Order._collection.find({'shipping.shipment': shipment.id})

        return dict(orders=orders, **dict(shipment))

#class CurrentShipment(Resource):
#    def get(self):
#        current = models.Shipment.get_current()
#        if not current.exists:
#            return "NOT FOUND", 404
#        orders = Order.find({'shipping': {'shipment': current.id}})
#
#        return dict(orders=orders, **dict(current))


def register_resources(admin_api):
    admin_api.add_resource(Shipments, '/shipments')
    #admin_api.add_resource(CurrentShipment, '/shipments/current')
    admin_api.add_resource(Shipment, '/shipments/<ObjectID:_id>')
