import json

from django.core.mail import EmailMessage

from apps.gh.minio.utils import MINIO_CLIENT
from libs import json_response
from spug import settings
from spug.overrides import MINIO_STORAGE_BUCKET_NAME


def send_email(request):
    if request.method == 'POST':
        info = json.loads(request.body.decode())
        subject = info['subject']
        message = info['message']
        recipient_list = info['recipient']
        file_names = info['file_names']

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_list,
            reply_to=[settings.EMAIL_HOST_USER],
        )
        try:
            for file_name in file_names:
                file_data = MINIO_CLIENT.get_object(MINIO_STORAGE_BUCKET_NAME, file_name)
                email.attach(file_name, file_data.read(), 'application/octet-stream')
            email.send()
            return json_response("邮件发送成功")
        except Exception as e:
            return json_response(error=e)
