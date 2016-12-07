from flask import url_for
from datetime import datetime
from gridfs import GridFS

from ...database import db, Document, ValidationError

class Product(Document):
    _collection = db.products
    _schema = [
        'description',
        'datetime',
        'cost',
        'stock',
        'name',
        'recipes', # ['name', 'url']
        'thumbnail'
    ]
    _check = _schema[:-1]

    @staticmethod
    def _format_new(**kwargs):
        return {
            **kwargs,
            'datetime': datetime.now()
        }

    @property
    def categories(self):
        p2cs = ProductToCategory.find(product=self._id)
        for p2c in p2cs:
            yield Category(p2c['category'])

    @property
    def thumbnail(self):
        fs = GridFS(db)
        return fs.get(self['thumbnail'])

    @thumbnail.setter
    def thumbnail(self, image):
        fs = GridFS(db)
        image_id = fs.put(image)
        self._doc['thumbnail'] = image_id
        self._update()


class Category(Document):
    _collection = db.categories
    _schema = [
        # '_id'
    ]

    @staticmethod
    def _format_new(**kwargs):
        name = kwargs['name']
        for char in name:
            if not char.isalnum() and char != ' ':
                raise ValidationError(
                    "Invalid character in category name: {}"
                        .format(char)
                )

        _id = name.lower().replace(' ', '-')
        cat = Category(_id)
        if cat.exists:
            raise ValidationError(
                "Category name too similar to existing category: {}"
                    .format(cat.name)
            )

        return {'_id': _id}

    @classmethod
    def find_by_name(cls, name):
        _id = name.lower().replace(' ', '-')
        return cls(_id)

    @property
    def name(self):
        return self._doc._id.replace('-', '-').title()

    @property
    def products(self):
        p2cs = ProductToCategory.find(category=self._id)

        for p2c in p2cs:
            yield Product(p2c['product'])

    @property
    def url(self):
        return url_for('products.view', category=self._id)

class ProductToCategory(Document):
    _collection = db.products_to_categories
    _schema = [
        'product',
        'category'
    ]

    @staticmethod
    def _format_new(**kwargs):
        product = kwargs['product']
        category = kwargs['category']

        return {
            'product': product._id,
            'category': category._id
        }


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
        kwargs['user'] = User(kwargs['user'])
        kwargs['datetime'] = datetime.now()
        return kwargs