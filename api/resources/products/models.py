from flask import url_for
from datetime import datetime

from ...database import db, Document, ValidationError


def user_and_review_import():
    from ..users.models import User
    global User

PLACEHOLDER_IMAGE_URL = '/images/placeholder.jpg'

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
    def url_name(self):
        """
        URL Safe name
        """
        return '-'.join(self['name'].lower().split())

    def __iter__(self):
        from ..reviews.models import Review

        yield 'categories', {
            cat.id: cat.name for cat in self.categories
        }

        yield 'reviews', map(dict, Review.find(product=self))

        for k, v in super(Product, self).__iter__():
            if k == 'images' and not v:
                yield k, [PLACEHOLDER_IMAGE_URL]
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
