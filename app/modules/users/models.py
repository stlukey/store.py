from ...models import BaseDocument, AutorefsDocument, db_register
from datetime import datetime


@db_register
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


@db_register
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


@db_register
class DefaultAddresses(AutorefsDocument):
    __collection__ = 'default_addresses'
    structure = {
        'user': User,
        'billing': Address,
        'shipping': Address
    }
    required_feilds = structure.keys()
