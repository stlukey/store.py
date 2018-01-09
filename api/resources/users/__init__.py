from flask import request, make_response
from ...utils import Resource, check_data
from .models import *
from validate_email import validate_email

from ...emails import email_activation, recovery_email

from .activation import confirm_email_token
from ...utils import JSONResponse

import datetime

ERROR_EMAIL_INVALID = "The entered email address is invalid. Please try again."
ERROR_EMAIL_CONFLICT = "That email already exists."
ERROR_BAD_LOGIN = "Incorrect email/password. Please try again."
ERROR_NOT_ACTIVATED = "Account not activated. Please check your email."
ERROR_BAD_EMAIL_TOKEN = "Email token invalid. Please try again."
ERROR_RECOVERY_NO_EMAIL = "No email entered. Please try again."

ACCOUNT_CREATED_MESSAGE = \
"""Account Created.
Please check your email for an activation link."""
ACCOUNT_ACTIVATED_MESSAGE = \
"Account activated. Please login."
RECOVER_EMAIL_SENT = \
"""If a matching account was found,
a password reset link has been emailed to:
{}"""
PASSWORD_CHANGED = \
"Your password was updated. Please login. "
LOGIN_SUCCESS = \
"Login successful."

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
                return ERROR_EMAIL_CONFLICT, 409

            # If user has not activated email for more than 24 hours.
            user.delete()

        if not validate_email(data['_id']):
            return ERROR_EMAIL_INVALID, 400

        data['first_name'] = data['first_name'].title()
        data['last_name'] = data['last_name'].title()


        user = User.new(**data)
        email_activation(user.id)
        return ACCOUNT_CREATED_MESSAGE, 200

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
            return ERROR_BAD_LOGIN, 401

        data = request.get_json(force=True)
        password = data.get('password')
        if password:
            password = user.check_password(password)
        if not password:
            return ERROR_BAD_LOGIN, 401

        if not user['active']:
            return ERROR_NOT_ACTIVATED, 401

        return (user.encode_auth_token().decode(), LOGIN_SUCCESS), 200

class ConfirmEmail(Resource):
    def post(self, email_token):
        email = confirm_email_token(email_token)
        if not email:
            return ERROR_BAD_EMAIL_TOKEN, 400

        user = User(email)
        user.update({'active': True})

        return ACCOUNT_ACTIVATED_MESSAGE, 200

class RecoverPassword(Resource):
    def post(self, email):
        if not email or email == "undefined":
            return ERROR_RECOVERY_NO_EMAIL, 400

        user = User(email)
        if user.exists:
            recovery_email(user.id)

        return RECOVER_EMAIL_SENT.format(email)

    def put(self, email):
        REQUIRED = [
            'password',
        ]
        email = confirm_email_token(email)
        if not email:
            return ERROR_BAD_EMAIL_TOKEN, 400

        user = User(email)
        if not user.exists:
            return ERROR_BAD_EMAIL_TOKEN, 400

        data = request.get_json(force=True)
        allowed, resp = check_data(data, REQUIRED, REQUIRED)
        if not allowed:
            return resp

        data['password'] = bcrypt.hash(data['password'])
        user.update(data)

        return PASSWORD_CHANGED


def register_resources(api):
    api.add_resource(Users, '/user')
    api.add_resource(ConfirmEmail, '/confirm/<string:email_token>')
    api.add_resource(RecoverPassword, '/recover/<email>')

    api.add_resource(UserToken, '/token/<email>')
