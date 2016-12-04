
from ...models import PartialConnection, BaseDocument, AutorefsDocument
from datetime import datetime

conn = PartialConnection()


@conn.register
class Product(BaseDocument):
    __collection__ = 'products'
    structure = {
        'name': str,
        'cost': float,
        'date_added': datetime,
        'description': str,
        'stock': int,
        'recipes': [{
            'name': str,
            'url': str
        }]
    }
    default_feilds = {
        'date_added': datetime.now
    }
    required_feilds = structure.keys()
    gridfs = {
        'containers': [
            'images'
        ]
    }

    @classmethod
    def find_by_cat(cls):
        return cls.find(cls)


@conn.register
class Category(BaseDocument):
    __collection__ = 'categories'
    structure = {
        'name': str
    }
    required_feilds = ['name']


@conn.register
class ProductToCategory(AutorefsDocument):
    __collection__ = 'products_to_categories'
    structure = {
        'product': Product,
        'category': Category
    }
    required_feilds = structure.keys()
