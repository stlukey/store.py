from flask import request

from ..utils import check_data, Resource, JSONResponse
from ..resources.mailing_list.models import Subscriber
from ..emails import send_email

from ..config import JS_ORIGIN

EMAIL_SENT_MESSAGE = \
"Email sent successfully."

EMAIL_FOOTER = """
<br />
<br />
<i>You are receiving this email because you are part of Maryam's Persian Pantry Mailing List.</i>
<a href="{unsubscribe}">Click here to unsubscribe</a> or go to: {unsubscribe}
"""

class Subscribers(Resource):
    def get(self):
        return list(Subscriber.find())

class SendMail(Resource):
    def post(self):
        REQUIRED = ['content', 'subject']
        data = request.get_json(force=True)
        # Check product data.
        allowed, resp = check_data(data, REQUIRED, REQUIRED)
        if not allowed:
            return resp

        for subscriber in Subscriber.find():
            url = JS_ORIGIN + '/unsubscribe/' + subscriber['email']
            send_email(data['subject'],
                       subscriber['email'],
                       data['content'] + EMAIL_FOOTER.format(unsubscribe=url),
                       html=True)

        return EMAIL_SENT_MESSAGE, 200



def register_resources(admin_api):
    admin_api.add_resource(SendMail, '/sendmail')
    admin_api.add_resource(Subscribers, '/subscribers')
