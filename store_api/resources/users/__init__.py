from flask import request
from ...utils import Resource
from .models import *

def pass_user(func):
    def wrapper(*args, **kwargs):
        email = auth.username()
        user = User(email)
        return func(user, *args, **kwargs)
    return wrapper

class Users(Resource):
    _decorators = {
        'get': [auth.login_required, pass_user],
        'post': [],
        'put': [auth.login_required, pass_user],
 #       'delete': [auth.login_required, pass_user]
    }
    def get(self, user):
        return user

    def post(self):
        REQUIRED = [
            '_id', 'password',
            'first_name', 'last_name',
            'contact_number'
        ]
        data = request.get_json(force=True)

        if REQUIRED.keys() != data.keys():
            return "BAD REQUEST; provided values should be: {}".format(
                REQUIRED.keys()), 400
        if User(data['_id']).exists:
            return "Conflict; email already exists.", 409

        user = User.new(*data)
        return user

    def put(self, user):
        ALLOWED = [
            'password', 'first_name',
            'last_name', 'contact_number'
        ] 
        data = request.get_json(force=True)
        for k in data.keys():
            if k not in ALLOWED:
                return "BAD REQUEST; '{}' not allowed.".format(key), 400

        if 'password' in data.keys():
            data['password'] = bcrypt.hash(data['password']) 

        res = user.update(data)
        if not res['nModified']:
            return "SEVER ERROR; not modified.", 500

        return user

#    def delete(self, user):
#        pass

def register_resources(api):
    api.add_resource(Users, '/user')

