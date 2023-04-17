# Author: Wang Cen
# Date: 2023/4/16 16:32
# http://10.188.15.53:9123/api/auth/token/
import json

import requests
from django.core.cache import cache

from libs import json_response, JsonParser, Argument

"""
import requests

from django.http import JsonResponse

def get(request):
    url = 'xxx'  # 網址
    params = {'name': 'zhangsan', 'age': 18}
    response = requests.get(url=url, params=params)  # 用的是params
    return JsonResponse(response.text, safe=False)

import requests
from json import dumps
from django.http import JsonResponse

def post(request):
    url = 'xxx'  # url網址
    data = {'name': 'zhangsan', 'age': 18}
    data = json.dumps(data)
    response = requests.post(url=url, data)  # 用的是data
    return JsonResponse(response.text, safe=False)


"""


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
    return token


# 获取用户的数据库类型
def get_instance(request):
    # 获取当前操作人的角色
    roles = request.user.roles.all()
    env = 'prod'
    if '测试' in roles[0].name:
        env = 'test'

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
    params = {'instance_name__icontains': env}
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
def check(request):
    form, error = JsonParser(
        Argument('instance_id', type=int, help='请求参数instance_id不能为空'),
        Argument('db_name', type=str, help='请求参数数据库名称不能为空'),
        Argument('full_sql', type=str, help='请求参数sql内容不能为空'),
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
    # payload = {'instance_id': form.instance_id, 'resource_type': 'database'}
    response = requests.post(url=url, json=form, headers=headers)
    if response.status_code != 200:
        return json_response(error='sql检查失败，请联系管理员！')
    """
    {
  "workflow": {
    "workflow_name": "20230407",
    "demand_url": "API接口提交自动审核上线工单",
    "group_id": 1,
    "db_name": "gh_cloud_sys_dev172",
    "is_backup": true,
    "engineer": "wangcen",
    "run_date_start": "",
    "run_date_end": "",
    "instance": 1
  },
  "sql_content": "INSERT INTO user_info (user_id,account,password,email,phone,user_status,create_time,update_time,operator,desp,org_id,sex) VALUES ('USER_1212811','test2023','DDFAE87V56329D9CEEDV61394X0E496G9AABBTC5N7DJB79C',null, '13701189186', 2, '2023-03-29 11:54:06', '2023-03-29 11:54:06', 'admin', null, 'ORG_00034', 1);alter table user_info add remark varchar(32) null comment '备注测试字段';"
}
    """
    # TODO 增加返回对象 errlevel判断 0-正常 1-警告 2-异常
    return json_response(response.json())
