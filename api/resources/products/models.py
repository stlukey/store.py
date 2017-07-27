from flask import url_for
from datetime import datetime
from gridfs import GridFS

from ...database import db, Document, ValidationError


def user_and_review_import():
    from ..users.models import User
    global User


def upload_image(image):
    fs = GridFS(db)
    return fs.put(image)


def delete_image(image_id):
    fs = GridFS(db)
    return fs.delete(image_id)


def get_image(image_id):
    fs = GridFS(db)
    return fs.get(image_id)


class Product(Document):
    _collection = db.products
    _schema = [
        'description',
        'datetime',
        'cost',
        'stock',
        'name',
        'recipes',  # ['name', 'url']
        'images',
        'active',

        {
            'measurements': [
                'width',
                'depth',
                'length',
                'weight'
            ]
        }
    ]
    _check = _schema[:-1]

    @staticmethod
    def _format_new(**kwargs):
        return {
            **kwargs,
            'images': [],
            'datetime': datetime.now(),
            'active': False
        }

    @property
    def categories(self):
        return [Category(p2c['category'])
                for p2c in ProductToCategory.find(product=self.id)]

    @categories.setter
    def categories(self, category_ids):
        current = ProductToCategory.find(product=self.id)
        for p2c in current:
            if p2c['category'] not in category_ids:
                p2c.delete()

        for category in category_ids:
            if category not in current:
                cat = Category(category)
                if not cat.exists:
                    cat = Category.new(_id=category)

                ProductToCategory.new(product=self,
                                      category=cat)

    @property
    def thumbnail(self):
        return Product.get_image(self['images'][0])

    @thumbnail.setter
    def thumbnail(self, image):
        self.add_image(image, 0)

    def add_image(self, image, index=None):
        IMAGE_COUNT = len(self._doc['images'])

        image_id = upload_image(image)
        if index is None or (index not in range(IMAGE_COUNT)):
            if index is None:
                index = IMAGE_COUNT
            self._doc['images'].insert(index, image_id)

        else:
            delete_image(self._doc['images'][index])
            self._doc['images'][index] = image_id

        self.update()

    @property
    def url_name(self):
        """
        URL Safe name
        """
        return '-'.join(self['name'].lower().split())

    def __iter__(self):
        from ..reviews.models import Review
        changes = {
            'images': lambda imgs: [
                url_for('productimage', id=img)
                    for img in (imgs
                        # If item has no images a placeholder will
                        # be provided on request.
                        if len(imgs) else ['placeholder'])],
        }

        yield 'categories', {
            cat.id: cat.name for cat in self.categories
        }

        yield 'reviews', map(dict, Review.find(product=self))

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
        if 'name' in kwargs:
            name = kwargs['name']
            for char in name:
                if not char.isalpha() and char != ' ':
                    raise ValidationError(
                        "Invalid character in category name: {}"
                        .format(char)
                    )
            _id = name.lower().replace(' ', '-')

        else:
            _id = kwargs['_id']
            for char in _id:
                if not char.islower() and char != '-':
                    raise ValidationError(
                        "Invalid character in category _id: {}"
                        .format(char)
                    )

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
        return self.id.replace('-', ' ').title()

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


user_and_review_import()
