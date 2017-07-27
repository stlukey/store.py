
from datetime import datetime

from ...database import Document, db
from ...emails import order_dispatched

from ..orders.models import Order
from ..users.models import User


class Shipment(Document):
    _collection = db.shipments
    _schema = [
        'datetime',
        'dispatch_datetime'
    ]

    @staticmethod
    def _format_new(**kwargs):
        kwargs['datetime'] = datetime.now()
        return kwargs

    @classmethod
    def find(cls, _sort=False, *args, **kwargs):
        if not _sort:
            _sort = ('datetime', -1)
        return super().find(_sort, *args, **kwargs)

    @classmethod
    def get_current(cls):
    	return cls(dispatch_datetime={'$exists': False})

    def mark_as_dispatched(self):
        self.update({'dispatch_datetime': datetime.now()})

        orders = Order._collection.find({'shipping.shipment': self.id})
        orders = map(Order, orders)
        for order in orders:
            user = User(order['user'])
            order_dispatched(user, order)
