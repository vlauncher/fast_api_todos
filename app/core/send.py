import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings

env = Environment(loader=FileSystemLoader("app/templates/email"))

def send_email(to: str, subject: str, template_name: str, context: dict):
    template = env.get_template(template_name)
    html_content = template.render(context)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_HOST_USER}>"
    msg["To"] = to
    msg.set_content(html_content, subtype="html")

    smtp_class = smtplib.SMTP_SSL if settings.EMAIL_USE_SSL else smtplib.SMTP

    with smtp_class(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        if not settings.EMAIL_USE_SSL and settings.EMAIL_USE_TLS:
            server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
