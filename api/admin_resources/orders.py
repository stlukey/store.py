from ..utils import Resource
from ..resources.orders import models


class OrdersAdmin(Resource):
    def get(self):
        return models.Order.find()


def register_resources(admin_api):
    admin_api.add_resource(OrdersAdmin, '/orders')