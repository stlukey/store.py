
from datetime import datetime

from ...database import Document, db

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
