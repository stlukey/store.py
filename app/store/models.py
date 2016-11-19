#!/usr/bin/env python
"""
Data model.
"""

from mongokit import Document
from datetime import datetime

to_register = []
def register(document):
    to_register.append(document)
    return document

class BaseDocument(Document):
    use_dot_notation = True

class AutorefsDocument(BaseDocument):
    user_autorefs = True

@register
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

@register
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

@register
class DefaultAddresses(AutorefsDocument):
    __collection__ = 'default_addresses'
    structure = {
        'user': User,
        'billing': Address,
        'shipping': Address
    }
    required_feilds = structure.keys()

@register
class Image(Document):
    __collection__ = 'images'
    structure = {
        'path': str
    }
    required_feilds = ['path']

@register
class Product(Document):
    __collection__ = 'products'
    structure = {
        'name': str,
        'cost': float,
        'description': str,
        'stock': int,
    }
    required_feilds = structure.keys()

@register
class ProductImage(AutorefsDocument):
    __collection__ = 'product_images'
    structure = {
        'image': Image,
        'product': Product
    }
    required_feilds = structure.keys()

@register
class ThumbnailImage(ProductImage):
    __collection__ = 'thumbnail_images' 
    structure = {
        'image': ProductImage,
    }

@register
class DisplayImage(ProductImage):
    __collection__ = 'display_images'
    structure = {
        'image': ProductImage,
    }

@register
class Payment(BaseDocument):
    __collection__ = 'payments'
    structure = {
        'amount': float,
        'currency': str,
        'ref': str,
        'datetime': datetime
    }
    required_feilds = structure.keys()
    default_values = {
        'currency': 'GBP',
        'datetime': datetime.now
    }

@register
class Shipment(BaseDocument):
    __collections__ = 'shipments'
    structure = {
        'create_time': datetime,
        'dispatch_time': datetime
    }
    default_values = {
        'create_time': datetime.now
    }

@register
class Order(AutorefsDocument):
    __collections__ = 'orders'
    structure = {
        'user': User,
        'datetime': datetime,
        'billing_address': Address,
        'shipping_address': Address,
        'payment': Payment,
    }
    required_feilds = structure.keys()
    default_values = {
        'datetime': datetime.now
    }

@register
class ShippedOrder(AutorefsDocument):
    __collections__ = 'shipped_orders'
    structure = {
        'shipment': Shipment,
        'order': Order,
        'tacking_id': str,
    }
    required_feilds = structure.keys()

@register
class OrderItems(AutorefsDocument):
    __collections__ = 'order_items'
    structure = {
        'order': Order,
        'product': Product,
        'amount': int
    }
    required_feilds = structure.keys()

