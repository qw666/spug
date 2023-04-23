import json

from django.core.mail import EmailMessage

from apps.gh.enum import SendStatus
from apps.gh.minio.utils import MINIO_CLIENT
from apps.gh.models import SendRecord, TestDemand, UserExtend
from libs import json_response
from spug import settings
from spug.overrides import MINIO_STORAGE_BUCKET_NAME


def send_email_req(request):
    if request.method == 'POST':
        info = json.loads(request.body.decode())
        subject = info['subject']
        message = info['message']
        recipient_list = info['recipient']
        file_names = info['file_names']
        record_item = {
            'status': 2,
            'user': request.user,
            'demand': TestDemand.objects.filter(pk=2).first()
        }
        return send_email(subject, message, recipient_list, file_names, record_item)

# 供内部调用
def send_email(subject, message, recipient_list, file_names, record_item):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        reply_to=[settings.EMAIL_HOST_USER],
    )

    email.to = list(UserExtend.objects.values_list('email', flat=True).filter(nickname__in=recipient_list))
    try:
        if file_names:
            for file_name in file_names:
                file_data = MINIO_CLIENT.get_object(MINIO_STORAGE_BUCKET_NAME, file_name)
                email.attach(file_name, file_data.read(), 'application/octet-stream')
        email.send()
        # 更新到发送记录表
        if record_item:
            content = f'主题:{subject}\n内容：{message}\n对应的文件附件：{file_names}' \
                if file_names else f'主题:{subject}\n内容：{message}'
            SendRecord.objects.create(
                sender=settings.EMAIL_HOST_USER,
                receiver=recipient_list,
                content=content,
                project_status=record_item['status'],
                send_status=SendStatus.SUCCESS.value,
                created_by=record_item['user'],
                test_demand=record_item['demand']
            )
        return json_response("邮件发送成功")
    except Exception as e:
        # 更新到发送记录表
        if record_item:
            content = f'主题:{subject}\n内容：{message}\n对应的文件附件：{file_names}'\
                if file_names else f'主题:{subject}\n内容：{message}'
            SendRecord.objects.create(
                sender=settings.EMAIL_HOST_USER,
                receiver=recipient_list,
                content=content,
                project_status=record_item['status'],
                send_status=SendStatus.FAILURE.value,
                created_by=record_item['user'],
                test_demand=record_item['demand']
            )
        return json_response(error=e)