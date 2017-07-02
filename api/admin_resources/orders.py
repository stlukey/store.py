from ..utils import Resource
from ..resources.orders import models

ERROR_ORDER_NOT_FOUND = "That order can not be found."

class OrdersAdmin(Resource):
    def get(self):
        return models.Order.find()

class OrderAdmin(Resource):
    def get(self, _id):
        order = models.Order(_id)
        if not order.exists:
            return ERROR_ORDER_NOT_FOUND, 404

        return order


def register_resources(admin_api):
    admin_api.add_resource(OrdersAdmin, '/orders')
    admin_api.add_resource(OrderAdmin, '/orders/<ObjectID:_id>')
