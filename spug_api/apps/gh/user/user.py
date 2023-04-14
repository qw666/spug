from apps.account.models import User, Role
from apps.gh.enum import RoleType
from libs import json_response


# 查询用户信息 type:1 开发人员   type:2 测试人员
def list_users(request):
    role_type: str = request.GET['role_type']
    users = []
    if int(role_type) == RoleType.DEV.value:
        for u in User.objects.filter(roles__name__contains='开发'):
            tmp = u.to_dict(excludes=('access_token', 'password_hash'))
            users.append(tmp)
    elif int(role_type) == RoleType.TEST.value:
        for u in User.objects.filter(roles__name__contains='测试'):
            tmp = u.to_dict(excludes=('access_token', 'password_hash'))
            users.append(tmp)
    else:
        for u in User.objects.all():
            tmp = u.to_dict(excludes=('access_token', 'password_hash'))
            users.append(tmp)
    return json_response(users)

