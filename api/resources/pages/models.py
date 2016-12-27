from ...database import db, Document


class Page(Document):
    _collection = db.pages
    _schema = [
        '_id',
        'content'
    ]
    _check = _schema
