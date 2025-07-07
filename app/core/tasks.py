from app.core.send import send_email
from app.core.celery_app import celery

@celery.task(name="app.core.tasks.send_email_task")
def send_email_task(to: str, subject: str, template_name: str, context: dict):
    send_email(to=to, subject=subject, template_name=template_name, context=context)
