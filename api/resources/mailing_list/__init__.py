from ...utils import Resource
from . import models

from validate_email import validate_email

ERROR_EMAIL_EXISTS =\
"Error: That email already exists."
ERROR_EMAIL_INVALID =\
"Error: The entered email address is invalid."
SUBSCRIBER_ADDED_MESSAGE =\
"Email added to mailing list."
SUBSCRIBER_REMOVED_MESSAGE =\
"Email removed from mailing list."

class Subscriber(Resource):
    def post(self, email):
        if not validate_email(email):
            return ERROR_EMAIL_INVALID, 400

        if models.Subscriber(email=email).exists:
            return ERROR_EMAIL_EXISTS, 400

        models.Subscriber.new(email=email)
        return SUBSCRIBER_ADDED_MESSAGE, 200

    def delete(self, email):
        subscriber = models.Subscriber(email=email)
        if subscriber.exists:
            subscriber.delete();

        return SUBSCRIBER_REMOVED_MESSAGE, 200



def register_resources(api):
    api.add_resource(Subscriber, '/subscriber/<email>')
