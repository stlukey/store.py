
from datetime import datetime

from ...models import BaseDocument, PartialConnection

conn = PartialConnection()

@conn.register
class Shipment(BaseDocument):
    __collections__ = 'shipments'
    structure = {
        'create_time': datetime,
        'dispatch_time': datetime
    }
    default_values = {
        'create_time': datetime.now
    }
