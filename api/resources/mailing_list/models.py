from datetime import datetime

from ..users.models import User

from ...database import db, Document

class Subscriber(Document):
    _collection = db.subscribers
    _schema = [
        'email',
        'datetime'
    ]
    _check = [
        'email'
    ]

    @staticmethod
    def _format_new(**kwargs):
        kwargs['datetime'] = datetime.now()
        return kwargs
