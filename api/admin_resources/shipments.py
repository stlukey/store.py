from flask import request
from ..utils import Resource, check_data
from ..resources.admin import models
from ..resources.orders.models import Order

ERROR_SHIPMENT_PENDING = "A shipment is already pending."
ERROR_NO_ORDERS_TO_SHIP = "No orders are awaiting shipment."
ERROR_NOTHING_TO_DISPATCH = "There is no pending shipment to mark as dispatched."
ERROR_SHIPMENT_NOT_FOUND = "That shipment can not be found."

class Shipments(Resource):
    def get(self):
        return models.Shipment.find()

    def post(self):
        """
        Put all pending orders in shipment.
        """
        current = models.Shipment.get_current()
        if current.exists:
            return ERROR_SHIPMENT_PENDING, 400


        orders_pending = Order.find_({'shipping.shipment': {'$exists': False}})
        if len(orders_pending) == 0:
            return ERROR_NO_ORDERS_TO_SHIP, 400

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
            return ERROR_NOTHING_TO_DISPATCH, 400

        current.mark_as_dispatched()

        return current

class Shipment(Resource):
    def get(self, _id):
        shipment = models.Shipment(_id)
        if not shipment.exists:
            return ERROR_SHIPMENT_NOT_FOUND, 404

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
