# app/Services/Mailing/server.py
import smtplib
import ssl
from email.message import EmailMessage


def sender(
    port: int,
    smtp_server: str,
    sender_email: str,
    receiver_email: str,
    password: str,
    subject: str,
    body: str,
):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)
