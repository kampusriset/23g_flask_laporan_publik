import smtplib
from email.message import EmailMessage
from flask import current_app

def send_email(subject, recipients, body):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    with smtplib.SMTP_SSL(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]) as server:
        server.login(
            current_app.config["MAIL_USERNAME"],
            current_app.config["MAIL_PASSWORD"],
        )
        server.send_message(msg)
