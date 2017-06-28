from ..utils import Resource
from ..resources.orders import models


class OrdersAdmin(Resource):
    def get(self):
        return models.Order.find()

class OrderAdmin(Resource):
    def get(self, _id):
        order = models.Order(_id)
        if not order.exists:
            return "NOT FOUND", 404

        return order


def register_resources(admin_api):
    admin_api.add_resource(OrdersAdmin, '/orders')
    admin_api.add_resource(OrderAdmin, '/orders/<ObjectID:_id>')