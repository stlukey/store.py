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
        'images'
    ]
    _check = _schema[:-1]

    @staticmethod
    def _format_new(**kwargs):
        return {
            **kwargs,
            'images': {},
            'datetime': datetime.now()
        }

    @property
    def categories(self):
        return [Category(p2c['category'])
                for p2c in ProductToCategory.find(product=self.id)]

    def get_image(self, image_name):
        fs = GridFS(db)
        return fs.get(self['images'][image_name])

    @property
    def thumbnail(self):
        return self.get_image('thumbnail')

    @thumbnail.setter
    def thumbnail(self, image):
        fs = GridFS(db)
        image_id = fs.put(image)
        self._doc['images']['thumbnail'] = image_id
        self.update()

    @property
    def url_name(self):
        """
        URL Safe name
        """
        return '-'.join(self['name'].lower().split())

    def __iter__(self):
        changes = {
            'images': lambda imgs: [url_for('productimage', id=self.id, name=img) for img in imgs.keys()],
        }

        yield 'categories', [
            [cat.id for cat in self.categories],
            [cat.name for cat in self.categories]
        ]

        for k, v in super(Product, self).__iter__():
            if k in changes:
                v = changes[k](v)
            yield k, v

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
        return self.id.replace('-', '-').title()

    @property
    def products(self):
        p2cs = ProductToCategory.find(category=self.id)

        for p2c in p2cs:
            yield Product(p2c['product'])

    @property
    def url(self):
        return url_for('products.view', category=self.id)

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
            'product': product.id,
            'category': category.id
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
