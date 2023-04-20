# Author: Wang Cen
# Date: 2023/4/16 16:32
# http://10.188.15.53:9123/api/auth/token/
import json
import logging

import requests
from django.core.cache import cache

from apps.gh.enum import Status, OrderStatus, ExecuteStatus, SqlExecuteStatus
from apps.gh.models import WorkFlow, SqlExecute, TestDemand
from libs import json_response, JsonParser, Argument, human_datetime


# 获取sql审核平台token
def get_auth_token(username):
    result = dict(token='', error='')
    unique_key = f'spug:archery:{username}'
    # 先从缓存中获取token
    cache_token = cache.get(unique_key)
    if cache_token:
        result['token'] = cache_token
        return result

    url = 'http://10.188.15.53:9123/api/auth/token/'
    password = 'gohigh@123'
    payload = {'username': username, 'password': password}
    response = requests.post(url=url, json=payload)

    if response.status_code != 200:
        result['error'] = '调用SQL审核平台服务异常，请联系管理员。'
        return result

    # 获取token
    token = response.json().get('access')

    if not token:
        result['error'] = '获取SQL审核平台token异常，请联系管理员。'
        return result

    cache.set(unique_key, token, 60 * 60 * 2)
    result['token'] = token
    return result


# 获取用户的数据库类型
def get_instance(request):
    # 获取当前提测申请的状态
    status = request.GET.get('status')
    if not status:
        status = 4

    username = request.user.username

    response_token = get_auth_token(username)
    token = response_token.get('token')
    if token is None:
        return json_response(error=response_token.get('error'))
    # 请求头中带有Authorization
    headers = {
        'Authorization': f'Bearer {token}'
    }

    url = 'http://10.188.15.53:9123/api/v1/instance/'
    params = {'instance_name__icontains': 'test' if int(status) == Status.TESTING.value else 'prod'}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return json_response(error='获取用户数据库实例失败，请联系管理员！')

    # TODO 增加返回对象
    return json_response(response.json().get('results'))


# 获取数据库实例下的资源信息
def get_resource(request):
    form, error = JsonParser(
        Argument('instance_id', type=int, help='请求参数instance_id不能为空')
    ).parse(request.GET)

    if error is not None:
        return json_response(error=error)

    username = request.user.username
    response_token = get_auth_token(username)
    token = response_token.get('token')
    if token is None:
        return json_response(error=response_token.get('error'))
    # 请求头中带有Authorization
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = 'http://10.188.15.53:9123/api/v1/instance/resource/'
    payload = {'instance_id': form.instance_id, 'resource_type': 'database'}
    response = requests.post(url=url, json=payload, headers=headers)
    if response.status_code != 200:
        return json_response(error='获取数据库实例下的资源信息失败，请联系管理员！')

    # TODO 增加返回对象
    return json_response(response.json().get('result'))


# SQL检查
#  post
def check_sql(request):
    form, error = JsonParser(
        Argument('instance', type=int, help='请求参数instance不能为空'),
        Argument('db_name', type=str, help='请求参数数据库名称不能为空'),
        Argument('sql_content', type=str, help='请求参数sql内容不能为空'),
    ).parse(request.body)

    if error is not None:
        return json_response(error=error)

    username = request.user.username
    response_token = get_auth_token(username)
    token = response_token.get('token')
    if token is None:
        return json_response(error=response_token.get('error'))
    # 请求头中带有Authorization
    headers = {
        'Authorization': f'Bearer {token}'
    }

    url = 'http://10.188.15.53:9123/api/v1/workflow/sqlcheck/'
    payload = {'instance_id': form.instance, 'db_name': form.db_name, 'full_sql': form.sql_content}
    response = requests.post(url=url, json=payload, headers=headers)
    if response.status_code != 200:
        return json_response(error='sql检查失败，请联系管理员！')
    # TODO 增加返回对象 errlevel判断 0-正常 1-警告 2-异常
    return json_response(response.json())


# SQL执行
def execute_sql(request):
    form, error = JsonParser(
        Argument('id', type=int, help='参数id不能为空'),
        Argument('demand_name', type=str, help='请输入需求名称'),
        Argument('demand_link', type=str, help='请输入需求链接'),
        Argument('status', type=int, help='当前工单的状态不能为空'),
        Argument('sql_exec_status', type=int, help='当前工单的sql执行状态不能为空'),
        Argument('databases', type=list, help='请选择待执行的sql工程信息')
    ).parse(request.body)

    if error is not None:
        return json_response(error=error)

    username = request.user.username
    response_token = get_auth_token(username)
    token = response_token.get('token')
    if token is None:
        return json_response(error=response_token.get('error'))
    # 请求头中带有Authorization
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # 清空当前工单对应的sql执行表
    SqlExecute.objects.filter(test_demand=form.id).delete()
    sql_exec_status = ExecuteStatus.TEST_EXECUTING.value if Status.TESTING.value == form.status else ExecuteStatus.PROD_EXECUTING.value

    try:
        for item in form.databases:
            # 调用sql提交接口
            url, payload = build_workflow_submit(form, item, username)
            response = requests.post(url=url, json=payload, headers=headers)
            if response.status_code != 201 or OrderStatus.WORKFLOW_MAN_REVIEWING.value != response.json().get(
                    'workflow').get('status'):
                # 更新当前的提测申请的sql执行状态
                if form.status == Status.TESTING.value:
                    sql_exec_status = ExecuteStatus.TEST_EXCEPTION.value
                else:
                    sql_exec_status = ExecuteStatus.PROD_EXCEPTION.value
                return json_response(error='sql申请失败，请联系管理员！')

            order_id = response.json().get('workflow').get('id')

            # 根据当前测试申请的状态 来判断是否需要自动审批
            if form.status == 2:
                # 调用sql审核接口
                url, payload = build_workflow_audit(order_id)
                response = requests.post(url=url, json=payload, headers=headers)
                if response.status_code != 200 or 'passed' != response.json().get('msg'):
                    # 更新当前的提测申请的sql执行状态
                    if form.status == Status.TESTING.value:
                        sql_exec_status = ExecuteStatus.TEST_EXCEPTION.value
                    else:
                        sql_exec_status = ExecuteStatus.PROD_EXCEPTION.value
                    create_sql_execute(order_id, SqlExecuteStatus.FAILURE.value, form, item, request)
                    return json_response(error='sql审核失败，请联系管理员！')

                # 调用sql执行接口
                url, payload = build_workflow_execute(order_id)
                response = requests.post(url=url, json=payload, headers=headers)
                if response.status_code != 200:
                    # 更新当前的提测申请的sql执行状态
                    if form.status == Status.TESTING.value:
                        sql_exec_status = ExecuteStatus.TEST_EXCEPTION.value
                    else:
                        sql_exec_status = ExecuteStatus.PROD_EXCEPTION.value
                    create_sql_execute(order_id, SqlExecuteStatus.FAILURE.value, form, item, request)

                    return json_response(error='sql执行失败，请联系管理员！')
            create_sql_execute(order_id, SqlExecuteStatus.SUCCESS.value, form, item, request)
        return json_response(data='success')
    except Exception as e:
        logging.error(e)
        # 更新当前的提测申请的sql执行状态
        if form.status == Status.TESTING.value:
            sql_exec_status = ExecuteStatus.TEST_EXCEPTION.value
        else:
            sql_exec_status = ExecuteStatus.PROD_EXCEPTION.value
        return json_response(error='sql执行失败，请联系管理员！')
    finally:
        # 更新当前的提测申请的sql执行状态
        work_flow = WorkFlow.objects.filter(test_demand=form.id).first()
        work_flow.sql_exec_status = sql_exec_status
        work_flow.updated_by = request.user
        work_flow.updated_at = human_datetime()
        work_flow.save()


def create_sql_execute(order_id, status, form, item, request):
    test_demand_id = TestDemand.objects.filter(pk=form.id).first()
    SqlExecute.objects.create(test_demand=test_demand_id,
                              order_id=order_id,
                              demand_name=item.get('db_name') + '_' + form.demand_name,
                              demand_link=form.demand_link,
                              sql_type=item.get('sql_type'),
                              group_id=item.get('group_id'),
                              instance=item.get('instance'),
                              db_type=item.get('db_type'),
                              db_name=item.get('db_name'),
                              status=status,
                              sql_content=item.get('sql_content'),
                              created_by=request.user
                              )


def build_workflow_execute(archery_workflow_id):
    url = 'http://10.188.15.53:9123/api/v1/workflow/execute/'

    payload = {
        "engineer": "chenqi",
        "workflow_id": archery_workflow_id,
        "workflow_type": 2,
        "mode": "auto"
    }
    return url, payload


def build_workflow_audit(archery_workflow_id):
    url = 'http://10.188.15.53:9123/api/v1/workflow/audit/'

    payload = {
        'engineer': 'chenqi',
        "workflow_id": archery_workflow_id,
        "audit_remark": "spug自动审核",
        "workflow_type": 2,
        "audit_type": "pass"
    }

    return url, payload


def build_workflow_submit(form, item, username):
    url = 'http://10.188.15.53:9123/api/v1/workflow/'

    disposition = {
        "workflow_name": item['db_name'] + '_' + form.demand_name,
        "demand_url": form.demand_link,
        "group_id": item['group_id'],
        "db_name": item['db_name'],
        "instance": item['instance'],
        "is_backup": True,
        "engineer": username
    }

    payload = {'workflow': disposition, 'sql_content': item['sql_content']}
    return url, payload
