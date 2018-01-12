from flask import render_template
import sendgrid
from sendgrid.helpers.mail import *

from .config import SERVER_EMAIL, SENDGRID_API_KEY, JS_ORIGIN
from .utils import async

from .resources.users.activation import generate_confirmation_token

import re
def cleanhtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

@async
def send_email(subject, to, content, html=False, no_template=False):
    HTML_TEMPLATE = "<html><body>{}</body></html>" if not no_template else "{}"

    mail = Mail()

    mail.from_email = Email(SERVER_EMAIL)
    mail.subject = subject

    personalization = Personalization()
    personalization.add_to(Email(to))
    mail.add_personalization(personalization)

    if html:
        content = HTML_TEMPLATE.format(content)
        mail.add_content(Content("text/plain", cleanhtml(content)))
        mail.add_content(Content("text/html", content))
    else:
        mail.add_content(Content("text/plain", content))


    return sg.client.mail.send.post(request_body=mail.get())




def items_in_cart(user):
    send_email("Complete Your Purchase",
               user.id,
               render_template("complete-purchase.txt",
                               user=user, items=sum(user['cart'].values())))

def order_confirmation(user, order):
    send_email("Order Confirmation",
               user.id,
               render_template("order-confirmation.txt",
                               user=user, order=order))

def order_dispatched(user, order):
    send_email("Order Dispatched",
               user.id,
               render_template("order-dispatched.txt",
                               user=user, order=order))



def email_activation(email):
    email_token = generate_confirmation_token(email)
    return send_email("User Account Activation",
               email,
               render_template("activation.txt",
                               email_token=email_token))

def recovery_email(email):
    email_token = generate_confirmation_token(email)
    return send_email("Reset password",
               email,
               render_template("reset.txt",
                               email_token=email_token))

def mailing_list_confirmation(email):
    unsubscribe = JS_ORIGIN + '/unsubscribe/' + email
    return send_email("Added to our mailing list.",
                      email,
                      render_template("mailing_list_confirmation.html",
                                      unsubscribe=unsubscribe),
                      html=True)
