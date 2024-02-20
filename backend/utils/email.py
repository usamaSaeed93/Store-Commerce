import os

from django.core.mail import EmailMessage
from django.template.loader import get_template
from dotenv import load_dotenv

load_dotenv()
home_url = os.getenv("SERVER_URL")
html_tmp_path = "email/email.html"
sender = "admin@orangestorage.com"


def send_client_email(msg_title, msg_html, sender, recipients):
    email_msg = EmailMessage(msg_title, msg_html, sender, recipients)
    email_msg.content_subtype = "html"
    email_msg.send(fail_silently=False)


def send_email(reset_code, email, id, passowrd):
    msg_title = "Reset your password."
    url = f"{home_url}/auth/resetpasswordhandler?code={reset_code}&id={id}&pass={passowrd}"
    link_expiry = "The link will expire in 5 minutes."
    message = (
        "Your password was recently requested to be reset. \n " "To confirm, go to\n"
    )
    button_text = "Click to reset"
    context_data = {
        "email": email,
        "url": url,
        "message": message,
        "button_txt": button_text,
        "link_expiry": link_expiry,
    }
    msg_html = get_template(html_tmp_path).render(context_data)
    send_client_email(msg_title, msg_html, sender, [email])


def send_verification_email(email, id):
    url = f"{home_url}/auth/verifyuser?id={id}"
    message = (
        "Thank You for registering to orage-store, "
        "Please verify your email address to continue"
    )
    button_text = "Click to verify"
    context_data = {
        "email": email,
        "url": url,
        "message": message,
        "button_txt": button_text,
    }
    msg_html = get_template(html_tmp_path).render(context_data)
    msg_title = "Verification"
    send_client_email(msg_title, msg_html, sender, [email])


def send_order_email(context_data):
    html_tmp_path = "orders/end-user.html"
    msg_html = get_template(html_tmp_path).render(context_data)
    msg_title = "Order Confirmation"
    send_client_email(msg_title, msg_html, sender, [context_data["email"]])


def send_admin_order_email(context_data):
    html_tmp_path = "orders/admin-user.html"
    msg_html = get_template(html_tmp_path).render(context_data)
    msg_title = "Order Confirmation"
    send_client_email(
        msg_title,
        msg_html,
        sender,
        [context_data["email"], context_data["provider_email"]],
    )


def send_order_email_user(context_data):
    html_tmp_path = "orders/order-continue.html"
    msg_html = get_template(html_tmp_path).render(context_data)
    if context_data["pending"] and context_data["completed"]:
        msg_title = "Order Completed Email"
    elif context_data["pending"]:
        msg_title = "Order Pending Email"
    send_client_email(msg_title, msg_html, sender, [context_data["email"]])
