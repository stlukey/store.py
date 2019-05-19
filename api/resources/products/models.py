from flask import url_for
from datetime import datetime

from ...database import db, Document, ValidationError

# Avoid circular import.
def user_and_review_import():
    from ..users.models import User
    from ..reviews.models import Review
    global User
    global Review

PLACEHOLDER_IMAGE_URL = '/images/placeholder.jpg'

class Product(Document):
    # Collection name.
    _collection = db.products
    
    # Dooument Feilds
    _schema = [
        'description',
        'datetime',
        'cost',
        'stock',
        'name',
        'recipes',  # Recipe(['name', 'url'])
        'images',
        'active',
        'related',

        { # Embeded Document.
            'measurements': [
                'width',
                'depth',
                'length',
                'weight'
            ]
        }
    ]
    # Everything but embedded document is required.
    _check = _schema[:-1]

    @staticmethod
    def _format_new(**kwargs):
        """
        On creation, set defaults.
        """
        return {
            **kwargs,
            'images': [],
            'datetime': datetime.now(),
            'related': {},
            'active': False
        }
    
    # End of MinimalMongo defintions.

    @property
    def categories(self):
        """
        Load categories for product, many to many relationship.
        """
        return [Category(p2c['category'])
                for p2c in ProductToCategory.find(product=self.id)]

    @categories.setter
    def categories(self, category_ids):
        """
        Save categories for product, many to many relationship.
        """
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
    def url_name(self):
        """
        URL Safe name
        """
        return '-'.join(self['name'].lower().split())

    def __iter__(self):
        """
        Yeild images, categories and reviews when iterated.
        """
        yield 'images', self._doc['images'] if self._doc['images'] else [PLACEHOLDER_IMAGE_URL]

        yield 'categories', {
            cat.id: cat.name for cat in self.categories
        }

        yield 'reviews', map(dict, Review.find(product=self))

        for k, v in super(Product, self).__iter__():
            if k != 'images':
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
