#!/usr/bin/env python
"""
Data model.
"""

from mongokit import Document
from datetime import datetime

to_register = []


def register_doc(document):
    to_register.append(document)
    return document


class BaseDocument(Document):
    __database__ = 'store'
    __collection__ = 'store'
    use_dot_notation = True


class AutorefsDocument(BaseDocument):
    user_autorefs = True


@register_doc
class User(BaseDocument):
    __collection__ = 'users'
    structure = {
        'email': str,
        'password': str,
        'first_name': str,
        'last_name': str,
        'contact_num': str,
        'create_time': datetime
    }
    default_values = {
        'create_time': datetime.now
    }
    required_feilds = [
        'email',
        'password',
        'first_name',
        'last_name',
        'contact_num'
    ]


@register_doc
class Address(AutorefsDocument):
    __collection__ = 'addresses'
    structure = {
        'user': User,
        'full_name': str,
        'line1': str,
        'line2': str,
        'line3': str,
        'city': str,
        'county': str,
        'postcode': str
    }
    required_feilds = {
        'user',
        'full_name',
        'line1',
        'city',
        'county',
        'postcode'
    }


@register_doc
class DefaultAddresses(AutorefsDocument):
    __collection__ = 'default_addresses'
    structure = {
        'user': User,
        'billing': Address,
        'shipping': Address
    }
    required_feilds = structure.keys()


@register_doc
class Product(BaseDocument):
    __collection__ = 'products'
    structure = {
        'name': str,
        'cost': float,
        'description': str,
        'stock': int,
        'links': [{
            'name': str,
            'url': str
        }]
    }
    required_feilds = structure.keys()
    gridfs = {
        'files': ['thumbnail'],
        'containers': [
            'display_images',
            'other_images',
        ]
    }


@register_doc
class Category(BaseDocument):
    __collection__ = 'categories'
    structure = {
        'name': str
    }
    required_feilds = ['name']


@register_doc
class ProductToCategory(AutorefsDocument):
    __collection__ = 'products_to_categories'
    structure = {
        'product': Product,
        'category': Category
    }
    required_feilds = structure.keys()


@register_doc
class Shipment(BaseDocument):
    __collections__ = 'shipments'
    structure = {
        'create_time': datetime,
        'dispatch_time': datetime
    }
    default_values = {
        'create_time': datetime.now
    }


@register_doc
class Order(AutorefsDocument):
    __collections__ = 'orders'
    structure = {
        'user': User,
        'datetime': datetime,
        'payment': {
            'address': Address,
            'amount': float,
            'currency': str,
            'ref': str,
            'datetime': datetime
        },
        'shipping': {
            'address': Address,
            'method': int,
            'shipment': Shipment,
            'tracking_id': str,
        },
        'items': [{
            'product': Product,
            'quantity': int,
        }]
    }
    required_feilds = [
        'user',
        'datetime',
        'payment',
        'shipping.address',
        'shipping.method',
        'items'
    ]
    default_values = {
        'datetime': datetime.now,
        'payment.datetime': datetime.now,
        'payment.currency': 'GBP',
    }
