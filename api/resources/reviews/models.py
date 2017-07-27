from datetime import datetime

from ..users.models import User

from ...database import db, Document

class Review(Document):
    _collection = db.reviews
    _schema = [
        'user',
        'rating',
        'description',
        'datetime'
    ]
    _check = [
        'rating',
        'description'
    ]

    @staticmethod
    def _format_new(**kwargs):
        kwargs['datetime'] = datetime.now()
        return kwargs

    def __iter__(self):
        yield 'user', User(self._doc['user'])._doc['first_name'].title()
        for k, v in super().__iter__():
            if k != 'user':
                yield k, v
