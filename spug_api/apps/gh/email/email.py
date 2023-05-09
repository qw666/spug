import json
from email.mime.text import MIMEText

import requests
from django.core.mail import EmailMessage

from apps.account.models import User
from apps.deploy.models import DeployRequest
from apps.gh.enum import SendStatus
from apps.gh.minio.utils import MINIO_CLIENT
from apps.gh.models import SendRecord, TestDemand, UserExtend
from apps.host.models import Host
from libs import json_response, human_datetime
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
        return send_email(subject, message, recipient_list, record_item, file_names)


# 供内部调用
def send_email(subject, message, recipient_list, record_item, file_names=None, html_names=None):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        reply_to=[settings.EMAIL_HOST_USER],
    )

    # table_html = os.path.dirname(os.path.abspath(__file__)) + '\\table.html'
    # table_html_str = open(table_html, 'rb').read()
    # content_html = MIMEText(table_html_str, "html", "utf-8")
    # email.attach(content_html)

    try:
        recipient_list = list(UserExtend.objects.values_list('email', flat=True).filter(nickname__in=recipient_list))
        email.to = recipient_list
        if file_names:
            for file_name in file_names:
                file_data = MINIO_CLIENT.get_object(MINIO_STORAGE_BUCKET_NAME, file_name)
                email.attach(file_name, file_data.read(), 'application/octet-stream')
        if html_names:
            for html_name in html_names:
                html_data = MINIO_CLIENT.get_object(MINIO_STORAGE_BUCKET_NAME, html_name)
                html = html_data.read()
                email.attach(MIMEText(html, "html", "utf-8"))
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
            content = f'主题:{subject}\n内容：{message}\n对应的文件附件：{file_names}' \
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


# 应用发布发邮件方法
def send_email_message(subject, message, recipient_list):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        reply_to=[settings.EMAIL_HOST_USER],
    )
    email.to = list(UserExtend.objects.values_list('email', flat=True).filter(nickname__in=recipient_list))
    email.send()


# 应用发布webhook调用
def send_deploy_email(request):
    deploy_request = json.loads(request.body)
    print(deploy_request)
    version = deploy_request['version'].split('#')[0]
    spug_app_name = deploy_request['app_name']
    spug_env_name = deploy_request['env_name']
    spug_target_name_list = [target['name'] for target in deploy_request['targets']]
    spug_req_name = deploy_request['req_name']
    spug_approve_by = deploy_request['approve_by']
    spug_created_by = deploy_request['created_by']
    spug_do_by = deploy_request['do_by']
    deploy_status = deploy_request['status']
    action = deploy_request['action']
    reason = deploy_request['reason']

    texts = [
        f'申请标题： {spug_req_name}',
        f'应用名称： {spug_app_name}',
        f'应用分支： {version}',
        f'发布环境： {spug_env_name}',
        f'发布主机： {spug_target_name_list}',
    ]

    if action == 'approve_req':
        notifiers = list(
            User.objects.values_list('nickname', flat=True).filter(roles__name__contains='管理').distinct())
        # notifiers = ['高银肖']
        title = '【spug通知】发布审核申请通知'
        texts.insert(0, '## %s' % '发布审核申请')
        texts.extend([
            f'申请人员： {spug_created_by}',
            f'申请时间： {human_datetime()}',
            '> 来自 Spug运维平台'
        ])
    elif action == 'approve_rst':
        notifiers = list(set([spug_created_by]))
        title = '【spug通知】审核结果通知'
        text = '通过' if deploy_status == '1' else '驳回'
        texts.insert(0, '## %s' % '发布审核结果')
        texts.extend([
            f'审核人员： {spug_approve_by}',
            f'审核结果： {text}',
            f'审核意见： {reason or ""}',
            f'审核时间： {human_datetime()}',
            '> 来自 Spug运维平台'
        ])
    else:
        notifiers = list(set([spug_created_by, spug_do_by]))
        title = '【spug通知】发布结果通知'
        text = '成功' if deploy_status == '3' else '失败'
        texts.insert(0, '## %s' % '发布结果通知')
        if spug_approve_by:
            texts.append(f'审核人员： {spug_approve_by}')
        texts.extend([
            f'执行人员： {spug_do_by}',
            f'发布结果： {text}',
            f'发布时间： {human_datetime()}',
            '> 来自 Spug运维平台'
        ])
    send_msg = '\n'.join(texts)
    send_email_message(title, send_msg, notifiers)
    # -------------------spug原始通知格式---------------------

    return json_response()


def start_send_webhook(request):
    req = DeployRequest.objects.filter(pk=1).first()
    host_ids = json.loads(req.host_ids) if isinstance(req.host_ids, str) else req.host_ids
    data = {
        'action': 'approve_req',
        'req_id': req.id,
        'req_name': req.name,
        'app_id': req.deploy.app_id,
        'app_name': req.deploy.app.name,
        'env_id': req.deploy.env_id,
        'env_name': req.deploy.env.name,
        'status': req.status,
        'reason': req.reason,
        'version': req.version,
        'targets': [{'id': x.id, 'name': x.name} for x in Host.objects.filter(id__in=host_ids)],
        'is_success': req.status == '3',
        'created_at': human_datetime(),
        'created_by': req.created_by.nickname if req.created_by else None,
        'approve_by': req.approve_by.nickname if req.approve_by else None,
        'do_by': req.do_by.nickname if req.do_by else None,
    }

    requests.post("http://localhost:3000/api/gh/email/send_deploy_email/", json=data, timeout=15)
    return json_response('成功了')
