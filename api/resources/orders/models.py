from datetime import datetime
from ...database import Document, db

class Order(Document):
    _collection = db.orders
    _schema = [
        'user',
        'datetime',
        'items', # {'product': 'amount'}

        {
            'payment': [
                'amount',
                'currency',
                'id'
            ],
            'shipping': [
                'address',
                'method',
                'shipment'
            ]
        }
    ]
    _check = [
        'user',
        'payment',
        'items'
    ]

    @classmethod
    def find(cls, _sort=False, *args, **kwargs):
        if not _sort:
            _sort = ('datetime', -1)
        return super().find(_sort, *args, **kwargs)

    @staticmethod
    def _format_new(**kwargs):
        kwargs['user'] = kwargs['user'].id
        kwargs['datetime'] = datetime.now()

        if 'payment' not in kwargs:
            kwargs['payment'] = {}
        kwargs['payment']['currency'] = 'GBP'

        return kwargs

    def can_view(self, user):
        return user.admin or (self._doc['user'] == user.id)
