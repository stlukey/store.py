from datetime import datetime

from ..users.models import User

from ...database import db, Document

class Subscriber(Document):
    # Collection name.
    _collection = db.subscribers
    
    # Document Feilds.
    _schema = [
        'email',
        'datetime'
    ]
    
    # Required Feilds.
    _check = [
        'email'
    ]

    # On creation, add date.
    @staticmethod
    def _format_new(**kwargs):
        kwargs['datetime'] = datetime.now()
        return kwargs
