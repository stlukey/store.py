from flask import render_template
import sendgrid
from sendgrid.helpers.mail import *

from .config import SERVER_EMAIL, SENDGRID_API_KEY
from .utils import async

from .resources.users.activation import generate_confirmation_token

sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

#@async
def send_email(subject, to, content):
    from_email = Email(SERVER_EMAIL)
    to_email = Email(to)
    content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, content)
    return sg.client.mail.send.post(request_body=mail.get())


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
