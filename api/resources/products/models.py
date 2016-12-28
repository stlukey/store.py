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
        'recipes',  # ['name', 'url']
        'images',
        'active'
    ]
    _check = _schema[:-1]

    @staticmethod
    def _format_new(**kwargs):
        return {
            **kwargs,
            'images': [],
            'datetime': datetime.now(),
            'active': True
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

        print(current, category_ids)
        for category in category_ids:
            print(category)
            if category not in current:
                cat = Category(category)
                if not cat.exists:
                    cat = Category.new(category)

                ProductToCategory.new(product=self,
                                      category=cat)


    def get_image(self, image_index):
        fs = GridFS(db)
        return fs.get(self['images'][int(image_index)])

    @property
    def thumbnail(self):
        return self.get_image(0)

    @thumbnail.setter
    def thumbnail(self, image):
        fs = GridFS(db)
        image_id = fs.put(image)
        self._doc['images'].insert(0, image_id)
        self.update()

    def add_image(self, image):
        fs = GridFS(db)
        image_id = fs.put(image)
        self._doc['images'].append(image_id)
        self.update()

    @property
    def url_name(self):
        """
        URL Safe name
        """
        return '-'.join(self['name'].lower().split())

    def __iter__(self):
        changes = {
            'images': lambda imgs: [
                url_for('productimage', id=self.id, image_index=img)
                    for img in range(len(imgs)
                        # If item has no images a placeholder will
                        # be provided on request.
                        if len(imgs) else 1)],
        }

        yield 'categories', {
            cat.id: cat.name for cat in self.categories
        }

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
            for char in name:
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
