from ...database import fs
from ...database import db, Document

class Image(object):
    def __init__(self, image_id):
        self._id = image_id
        self.data = fs.get(image_id) if fs.exists(image_id) else None

    @staticmethod
    def new(data):
        image_id = fs.put(data)
        return Image(image_id)

    @staticmethod
    def _from_grid(f):
        image_id = f._id
        return Image(image_id)

    @staticmethod
    def find_all():
        return map(Image._from_grid, fs.find().sort("uploadDate", -1))

    def delete(self):
        return fs.delete(self._id)

    @property
    def url(self):
        return '/images/{}.jpg'.format(self._id)

    @property
    def exists(self):
        return self.data != None


    def __iter__(self):
        yield '_id', self._id
        yield 'url', self.url

class SetImage(Document):
    _collection = db.set_image
    _schema = [
        'image'
    ]
    _check = ['_id'] + _schema
