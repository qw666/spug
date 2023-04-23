# Author: Wang Cen
# Date: 2023/4/16 16:32
# http://10.188.15.53:9123/api/auth/token/
import json
import logging
import time

import requests
from django.core.cache import cache
from django.db.models import Max
from django.views import View

from apps.gh.enum import Status, OrderStatus, ExecuteStatus, SqlExecuteStatus, SyncStatus
from apps.gh.models import WorkFlow, SqlExecute, TestDemand, DatabaseConfig
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

    sql_exec_status = ExecuteStatus.TEST_EXECUTING.value \
        if Status.TESTING.value == form.status else ExecuteStatus.PROD_EXECUTING.value
    workflow_status = Status.ONLINE.value if Status.UNDER_ONLINE.value == form.status else Status.TESTING.value

    for item in form.databases:
        try:
            # 针对执行成功的过滤 不再执行
            if item.get('id'):
                execute = SqlExecute.objects.filter(pk=item.get('id'), status=SqlExecuteStatus.SUCCESS.value)
                if execute:
                    continue
                else:
                    # 删除执行中和执行失败的sql记录
                    execute.delete()

            # 调用sql提交接口
            archery_execute_status = SqlExecuteStatus.EXECUTING.value
            url, payload = build_workflow_submit(form, item, username)
            response = requests.post(url=url, json=payload, headers=headers)
            if response.status_code != 201 or OrderStatus.WORKFLOW_MAN_REVIEWING.value != response.json().get(
                    'workflow').get('status'):
                archery_execute_status = SqlExecuteStatus.FAILURE.value
                error = 'sql申请失败，请联系管理员！'
                continue

            order_id = response.json().get('workflow').get('id')

            # 根据当前测试申请的状态 来判断是否需要自动审批
            if form.status == 2:
                # 调用sql审核接口
                url, payload = build_workflow_audit(order_id)
                response = requests.post(url=url, json=payload, headers=headers)
                if response.status_code != 200 or 'passed' != response.json().get('msg'):
                    archery_execute_status = SqlExecuteStatus.FAILURE.value
                    error = 'sql审核失败，请联系管理员！'
                    continue

                # 调用sql执行接口
                url, payload = build_workflow_execute(order_id)
                response = requests.post(url=url, json=payload, headers=headers)
                if response.status_code != 200:
                    # 更新当前的提测申请的sql执行状态
                    archery_execute_status = SqlExecuteStatus.FAILURE.value
                    error = 'sql执行失败，请联系管理员！'
                    continue
        except Exception as e:
            logging.error(e)
            archery_execute_status = SqlExecuteStatus.FAILURE.value
            error = 'sql执行出现异常，请联系管理员！'
        finally:
            create_sql_execute(order_id, archery_execute_status, form, item, request)

    # 更新当前的提测申请的sql执行状态
    work_flow = WorkFlow.objects.filter(test_demand=form.id).first()
    work_flow.status = workflow_status
    work_flow.sql_exec_status = sql_exec_status
    work_flow.updated_by = request.user
    work_flow.updated_at = human_datetime()
    work_flow.save()
    return json_response(error=error)


def create_sql_execute(order_id, status, form, item, request):
    # 更新当前的提测申请的sql执行状态
    if form.status == Status.TESTING.value:
        env = 'test'
    else:
        env = 'prod'
    order_id = order_id if order_id else 0
    workflow_id = WorkFlow.objects.filter(test_demand=form.id).first()
    SqlExecute.objects.create(test_demand=workflow_id,
                              order_id=order_id,
                              sync_env=env,
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
    time_stamp = int(time.time())
    disposition = {
        "workflow_name": time_stamp + item['db_name'] + form.demand_name,
        "demand_url": form.demand_link,
        "group_id": item['group_id'],
        "db_name": item['db_name'],
        "instance": item['instance'],
        "is_backup": True,
        "engineer": username
    }

    payload = {'workflow': disposition, 'sql_content': item['sql_content']}
    return url, payload


# 获取sql执行结果
def get_workflow_result(request):
    # 先筛选需要更新的数据  更新sql执行状态
    executing_sql = list(SqlExecute.objects.filter(status=SqlExecuteStatus.EXECUTING.value))

    response_token = get_auth_token('chenqi')
    token = response_token.get('token')
    if token is None:
        return json_response(error=response_token.get('error'))
    # 请求头中带有Authorization
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = 'http://10.188.15.53:9123/api/v1/workflow/?page=1&size=10'
    workflow_ids = set()
    for item in executing_sql:
        params = {'workflow_id': item.get('order_id')}
        response = requests.get(url=url, params=params, headers=headers)

        if response.status_code != 200:
            logging.warning('定时任务:sql工单:' + item.get('demand_name') + '的执行状态失败')
            return
        elif response.json()['count'] == 0:
            logging.warning('定时任务:sql工单:' + item.get('demand_name') + '无需同步')
            return

        status = response.json()['results'][0]['workflow']['status']
        if OrderStatus.WORKFLOW_FINISH.value == status:
            item.status = SqlExecuteStatus.SUCCESS.value
        elif OrderStatus.WORKFLOW_ABORT.value == status or OrderStatus.WORKFLOW_AUTO_REVIEW_WRONG.value == status or OrderStatus.WORKFLOW_EXCEPTION.value == status:
            item.status = SqlExecuteStatus.FAILURE.value
        else:
            continue
        item.save

        workflow_ids.add(item.get('workflow_id'))

    # 更新workflow
    for workflow_id in workflow_ids:
        aggregate = SqlExecute.objects.filter(workflow_id=workflow_id).aggregate(max=Max('status'))
        max_status = aggregate.get('max')
        workflow = WorkFlow.objects.filter(pk=workflow_id).first()
        if workflow.get('is_sync') == SyncStatus.WAITING_SYNCHRONIZE.value:
            if workflow.get('status') == Status.ONLINE.value:
                if max_status == SqlExecuteStatus.FAILURE.value:
                    workflow.sql_exec_status = ExecuteStatus.PROD_EXCEPTION.value
                elif max_status == SqlExecuteStatus.SUCCESS.value:
                    workflow.sql_exec_status = ExecuteStatus.PROD_FINISH.value
                else:
                    workflow.sql_exec_status = ExecuteStatus.PROD_EXECUTING.value
            elif workflow.get('status') == Status.TESTING.value:
                if max_status == SqlExecuteStatus.FAILURE.value:
                    workflow.sql_exec_status = ExecuteStatus.TEST_EXCEPTION.value
                elif max_status == SqlExecuteStatus.SUCCESS.value:
                    workflow.sql_exec_status = ExecuteStatus.TEST_FINISH.value
                else:
                    workflow.sql_exec_status = ExecuteStatus.TEST_EXECUTING.value
        else:
            if max_status == SqlExecuteStatus.FAILURE.value:
                workflow.is_sync = SyncStatus.SYNCHRONIZE_EXCEPTION.value
            elif max_status == SqlExecuteStatus.SUCCESS.value:
                workflow.is_sync = SyncStatus.SYNCHRONIZE_FINISH.value
            else:
                workflow.is_sync = SyncStatus.SYNCHRONIZING.value
        workflow.save()


class SyncView(View):

    # 获取同步测试数据
    def get(self, request):
        form, error = JsonParser(
            Argument('id', type=int, help='请求参数提测申请id不能为空')
        ).parse(request.GET)

        if error is not None:
            return json_response(error=error)
        result = dict()
        workflow = WorkFlow.objects.filter(test_demand=form.id).first()

        executes = list(SqlExecute.objects.filter(workflow=workflow.id, env='test'))
        execute_env = {item.get('db_name').split(sep='_')[-1] for item in executes}

        result['execute_record'] = list(SqlExecute.objects.filter(workflow=workflow.id))
        result['sync_env'] = list(execute_env)

        return json_response(data=result, error=error)

    # 同步环境
    def post(self, request):
        form, error = JsonParser(
            Argument('id', type=int, help='参数id不能为空'),
            Argument('demand_name', type=str, help='请输入需求名称'),
            Argument('demand_link', type=str, help='请输入需求链接'),
            Argument('sync_finish', type=list, help='请输入已同步的环境'),
            Argument('sync_envs', type=list, help='请指定同步环境！'),
        ).parse(request.body)
        if error is not None:
            return json_response(error=error)

        # 校验sql哪些环境执行 和执行顺序
        workflow = WorkFlow.objects.filter(test_demand=form.id).first()

        need_sync_workflow = WorkFlow.objects.filter(status=Status.COMPLETE_ONLINE.ONLINE.value, is_sync=0)
        for item in list(need_sync_workflow):
            # parse_time
            if item.updated_at < workflow.updated_at:
                return json_response(error='请先同步' + workflow.test_demand.demand_name)

        difference_set = set(form.sync_envs).difference(set(form.sync_finish))
        if not difference_set:
            return json_response(error='没有需要同步的环境，请重新选择！')

        username = request.user.username
        response_token = get_auth_token('chenqi')
        token = response_token.get('token')
        if token is None:
            return json_response(error=response_token.get('error'))
        # 请求头中带有Authorization
        headers = {
            'Authorization': f'Bearer {token}'
        }
        url = 'http://10.188.15.53:9123/api/v1/instance/'
        params = {'instance_name__icontains': 'test'}
        response = requests.get(url=url, params=params, headers=headers)
        if response.status_code != 200:
            return json_response(error='获取用户数据库实例失败，请联系管理员！')

        instance_dict = {item.get('db_type'): item for item in response.json().get('results')}

        database_configs = list(DatabaseConfig.objects.filter(test_demand=form.id))
        for item in database_configs:
            url = 'http://10.188.15.53:9123/api/v1/workflow/'
            instance = instance_dict.get(item.db_type)
            time_stamp = int(time.time())
            for env in form.sync_envs:
                db_name = item.get('db_name') + '_' + env
                disposition = {
                    "workflow_name": time_stamp + db_name + form.demand_name,
                    "demand_url": form.demand_link,
                    "group_id": instance.get('resource_group')[0],
                    "db_name": db_name,
                    "instance": instance.get('id'),
                    "is_backup": True,
                    "engineer": username
                }
                payload = {'workflow': disposition, 'sql_content': item['sql_content']}

                response = requests.post(url=url, json=payload, headers=headers)
                if response.status_code != 201 or OrderStatus.WORKFLOW_MAN_REVIEWING.value != response.json().get(
                        'workflow').get('status'):
                    # 更新当前的提测申请的sql执行状态
                    create_sql_execute(0, SqlExecuteStatus.FAILURE.value, form, item, request)
                    return json_response(error='sql申请失败，请联系管理员！')

                order_id = response.json().get('workflow').get('id')
                url = 'http://10.188.15.53:9123/api/v1/workflow/audit/'
                payload = {
                    'engineer': 'chenqi',
                    "workflow_id": order_id,
                    "audit_remark": "spug自动审核",
                    "workflow_type": 2,
                    "audit_type": "pass"
                }
                response = requests.post(url=url, json=payload, headers=headers)
                if response.status_code != 200 or 'passed' != response.json().get('msg'):
                    create_sql_execute(order_id, SqlExecuteStatus.FAILURE.value, form, item, request)
                    return json_response(error='sql审核失败，请联系管理员！')

                url = 'http://10.188.15.53:9123/api/v1/workflow/execute/'
                payload = {
                    "engineer": "chenqi",
                    "workflow_id": order_id,
                    "workflow_type": 2,
                    "mode": "auto"
                }
                response = requests.post(url=url, json=payload, headers=headers)
                if response.status_code != 200:
                    create_sql_execute(order_id, SqlExecuteStatus.FAILURE.value, form, item, request)
                    return json_response(error='sql执行失败，请联系管理员！')
                create_sql_execute(order_id, SqlExecuteStatus.EXECUTING.value, form, item, request)

        workflow.status = SyncStatus.SYNCHRONIZING.value
        workflow.save()

        return json_response(data='success')

    # 手动执行SQL
    def patch(self, request):
        form, error = JsonParser(
            Argument('id', type=int, help='参数id不能为空'),
            Argument('sql_content', type=str, help='参数sql内容不能为空'),
        ).parse(request.body)
        if error is not None:
            return json_response(error=error)
        execute = SqlExecute.objects.filter(pk=form.id).first()
        username = request.user.username

        response_token = get_auth_token('chenqi')
        token = response_token.get('token')
        if token is None:
            return json_response(error=response_token.get('error'))
        # 请求头中带有Authorization
        headers = {
            'Authorization': f'Bearer {token}'
        }

        url = 'http://10.188.15.53:9123/api/v1/workflow/'
        time_stamp = int(time.time())
        disposition = {
            "workflow_name": time_stamp + execute.get('db_name') + form.demand_name,
            "demand_url": execute.get('demand_link'),
            "group_id": execute.get('group_id'),
            "db_name": execute.get('db_name'),
            "instance": execute.get('instance'),
            "is_backup": True,
            "engineer": username
        }
        payload = {'workflow': disposition, 'sql_content': form.sql_content}

        response = requests.post(url=url, json=payload, headers=headers)
        if response.status_code != 201 or OrderStatus.WORKFLOW_MAN_REVIEWING.value != response.json().get(
                'workflow').get('status'):
            # 更新当前的提测申请的sql执行状态
            update_execute_sql(1, SqlExecuteStatus.FAILURE.value, username)
            return json_response(error='sql申请失败，请联系管理员！')

        order_id = response.json().get('workflow').get('id')
        url = 'http://10.188.15.53:9123/api/v1/workflow/audit/'
        payload = {
            'engineer': 'chenqi',
            "workflow_id": order_id,
            "audit_remark": "spug同步sql 修改！",
            "workflow_type": 2,
            "audit_type": "pass"
        }
        response = requests.post(url=url, json=payload, headers=headers)
        if response.status_code != 200 or 'passed' != response.json().get('msg'):
            update_execute_sql(order_id, SqlExecuteStatus.FAILURE.value, username)
            return json_response(error='sql审核失败，请联系管理员！')

        url = 'http://10.188.15.53:9123/api/v1/workflow/execute/'
        payload = {
            "engineer": "chenqi",
            "workflow_id": order_id,
            "workflow_type": 2,
            "mode": "auto"
        }
        response = requests.post(url=url, json=payload, headers=headers)
        if response.status_code != 200:
            update_execute_sql(order_id, SqlExecuteStatus.FAILURE.value, username)
            return json_response(error='sql执行失败，请联系管理员！')

        update_execute_sql(order_id, SqlExecuteStatus.SUCCESS.value, username)

        pass


def update_execute_sql(order_id, status, username, execute):
    execute.status = status
    execute.order_id = order_id
    execute.created_by = username
    execute.save()

