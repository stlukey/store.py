from ...models import AutorefsDocument, PartialConnection

from datetime import datetime

from ..users.models import User, Address
from ..admin.models import Shipment

from ..products.models import Product

conn = PartialConnection()

@conn.register
class Order(AutorefsDocument):
    __collections__ = 'orders'
    structure = {
        'user': User,
        'datetime': datetime,
        'payment': {
            'address': Address,
            'amount': float,
            'currency': str,
            'ref': str,
            'datetime': datetime
        },
        'shipping': {
            'address': Address,
            'method': int,
            'shipment': Shipment,
            'tracking_id': str,
        },
        'items': [{
            'product': Product,
            'quantity': int,
        }]
    }
    required_feilds = [
        'user',
        'datetime',
        'payment',
        'shipping.address',
        'shipping.method',
        'items'
    ]
    default_values = {
        'datetime': datetime.now,
        'payment.datetime': datetime.now,
        'payment.currency': 'GBP',
    }
