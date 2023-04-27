import os

from apps.app.models import Deploy
from libs import auth
from apps.setting.utils import AppSetting
from libs import JsonParser, Argument, json_response
from libs.gitlib import Git
from spug import settings


# 查询项目服务列表
def list_apps(request):
    form, error = JsonParser(
        Argument('id', type=int, required=False)
    ).parse(request.GET)
    if error is None:
        apps = []
        deploy = Deploy.objects.filter(env__name__contains='94')
        for d in deploy:
            tmp = d.app.to_dict(selects=('id', 'name', 'key', 'desc'))
            tmp['deploy_id'] = d.id
            apps.append(tmp)
        return json_response(apps)
    return json_response(error=error)


# 查询应用版本号列表
@auth('deploy.app.config|deploy.repository.add|deploy.request.add|deploy.request.edit')
def get_versions(request, d_id):
    deploy = Deploy.objects.filter(pk=d_id).first()
    if not deploy:
        return json_response(error='未找到指定应用')
    if deploy.extend == '2':
        return json_response(error='该应用不支持此操作')
    branches, tags = fetch_versions(deploy)
    return json_response({'branches': branches, 'tags': tags})


def fetch_versions(deploy: Deploy):
    git_repo = deploy.extend_obj.git_repo
    repo_dir = os.path.join(settings.REPOS_DIR, str(deploy.id))
    pkey = AppSetting.get_default('private_key')
    with Git(git_repo, repo_dir, pkey) as git:
        return git.fetch_branches_tags()
