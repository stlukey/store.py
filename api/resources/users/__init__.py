from flask import request, make_response
from ...utils import Resource, check_data
from .models import *

from ...emails import email_activation

from .activation import confirm_email_token

import datetime

class Users(Resource):
    _decorators = {
        'get': [requires_token],
        'post': [],
        'put': [requires_token]
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
        allowed, resp = check_data(data, REQUIRED, REQUIRED)
        if not allowed:
            return resp


        user = User(data['_id'])
        if user.exists:
            if (user['active'] or
                user['datetime'] < datetime.datetime.now()
                                  -datetime.timedelta(days=1)):
                return "Conflict; email already exists.", 409

            # If user has not activated email for more than 24 hours.
            user.delete()


        user = User.new(**data)
        email_activation(user.id)
        return user

    def put(self, user):
        ALLOWED = [
            'password', 'first_name',
            'last_name', 'contact_number'
        ]
        data = request.get_json(force=True)
        allowed, resp = check_data(data, ALLOWED)
        if not allowed:
            return resp

        if 'password' in data.keys():
            data['password'] = bcrypt.hash(data['password'])

        res = user.update(data)
        #if not res['nModified']:
        #    return "SEVER ERROR; not modified.", 500

        return user


class UserToken(Resource):
    def post(self, email):
        user = User(email)
        if not user.exists:
            return "Authentication Error; no user", 401

        data = request.get_json(force=True)
        password = data.get('password')
        if password:
            password = user.check_password(password)
        if not password:
            return "Authentication Error; no pass", 401

        if not user['active']:
            return "Authentication Error; email not validated.", 401

        token = user.generate_auth_token()

        resp = make_response('{"message": "SUCCESS"}')
        resp.set_cookie('token', token)

        return resp

class ConfirmEmail(Resource):
    def post(self, email_token):
        email = confirm_email_token(email_token)
        if not email:
            return "Bad Request; email token invalid.", 400

        user = User(email)
        user.update({'active': True})
        return user


def register_resources(api):
    api.add_resource(Users, '/user')
    api.add_resource(ConfirmEmail, '/confirm/<string:email_token>')
    api.add_resource(UserToken, '/token/<string:email>')
