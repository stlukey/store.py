from ...database import db, Document


class Page(Document):
    _collection = db.pages
    _schema = [
        'content'
    ]
    _check = ['_id'] + _schema
