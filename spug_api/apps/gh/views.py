from threading import Thread

from django.db import transaction
from django.views import View

from apps.account.models import User
from apps.app.models import Deploy
from apps.deploy.models import DeployRequest
from apps.gh.app.app import fetch_versions
from apps.gh.email.email import send_email
from apps.gh.enum import Status, ExecuteStatus, SqlExecuteStatus
from apps.gh.helper import Helper
from apps.gh.models import TestDemand, WorkFlow, DevelopProject, DatabaseConfig
from apps.repository.models import Repository
from libs import json_response, JsonParser, Argument, human_datetime
import json

from spug import settings


# Create your views here.

class TestView(View):

    # 新增提测申请
    def post(self, request):
        form, error = JsonParser(
            Argument('demand_name', help='请输入需求名称'),
            Argument('demand_link', help='请输入需求链接'),
            Argument('developer_name', type=str, help='请输入开发人员'),
            Argument('tester_name', type=str, help='请输入测试人员'),
            Argument('projects', type=list, help='请选择工程信息'),
            Argument('databases', type=list, required=False)
        ).parse(request.body)

        if error is not None:
            return json_response(error=error)

        # 增加校验
        deploy_id_slist = [item.get('deploy_id') for item in form.projects]
        deploy_id_set = {item.get('deploy_id') for item in form.projects}
        if len(deploy_id_slist) != len(deploy_id_set):
            return json_response(error="该提测申请中包含相同的工程信息，请重新确认工程信息！")

        form.notify_name = form.developer_name + ',' + form.tester_name

        with transaction.atomic():

            test_demand_id = TestDemand.objects.create(demand_name=form.demand_name,
                                                       demand_link=form.demand_link,
                                                       created_by=request.user)

            batch_project_config = [DevelopProject(test_demand=test_demand_id,
                                                   deploy_id=item.get('deploy_id'),
                                                   app_name=item.get('app_name'),
                                                   branch_name=item.get('branch_name'),
                                                   created_by=request.user
                                                   )
                                    for item in form.projects]

            DevelopProject.objects.bulk_create(batch_project_config)

            if form.databases is not None:
                WorkFlow.objects.create(test_demand=test_demand_id,
                                        developer_name=form.developer_name,
                                        sql_exec_status=ExecuteStatus.TEST_WAITING.value,
                                        tester_name=form.tester_name,
                                        notify_name=form.notify_name,
                                        updated_by=request.user
                                        )

                batch_database_config = [DatabaseConfig(test_demand=test_demand_id,
                                                        db_type=item.get('db_type'),
                                                        instance=item.get('instance'),
                                                        db_name=item.get('db_name'),
                                                        group_id=item.get('group_id'),
                                                        sql_type=item.get('sql_type'),
                                                        sql_content=item.get('sql_content'),
                                                        created_by=request.user
                                                        )
                                         for item in form.databases]
                DatabaseConfig.objects.bulk_create(batch_database_config)
            else:
                WorkFlow.objects.create(test_demand=test_demand_id,
                                        developer_name=form.developer_name,
                                        tester_name=form.tester_name,
                                        sql_exec_status=ExecuteStatus.NO_NEED_EXECUTE.value,
                                        notify_name=form.notify_name,
                                        updated_by=request.user
                                        )

        # 提交测试申请 发邮件
        subject = f'【spug通知】（{test_demand_id.demand_name}）提测申请'
        message = f'（{test_demand_id.demand_name}）提测申请，请前往指定测试人员'
        recipient_list = form.notify_name.split(",")
        file_names = None
        record_item = {
            'status': Status.UNDER_TEST.value,
            'user': request.user,
            'demand': test_demand_id
        }
        Thread(target=send_email, args=(subject, message, recipient_list, file_names, record_item)).start()
        return json_response(data='success')

    # 查询提测申请
    def get(self, request):
        test_demands = []
        for item in TestDemand.objects.order_by('-created_at'):
            temp = item.to_dict(excludes=('created_by_id',))
            work_flow = item.workflow.to_dict(
                excludes=(
                    'id', 'test_demand_id', 'is_sync', 'sync_status', 'notify_name', 'created_by_id', 'created_at'))
            result = dict(temp, **work_flow)
            result['projects'] = list(item.projects.values('id', 'deploy_id', 'app_name', 'branch_name'))
            result['databases'] = list(
                item.databases.values('id', 'db_type', 'db_name', 'group_id', 'instance', 'sql_type',
                                      'sql_content'))

            test_demands.append(result)
        # 处理返回值
        return json_response(test_demands)

    # 删除提测申请
    def delete(self, request):
        form, error = JsonParser(
            Argument('id', type=int, help='请指定操作对象')
        ).parse(request.GET)
        if error is not None:
            return json_response(error=error)

        work_flow = WorkFlow.objects.filter(test_demand=form.id).first()

        if not work_flow:
            return json_response(error='未找到指定对象')

        if work_flow.status == Status.UNDER_TEST.value or work_flow.status == Status.DELEGATE_TEST.value:
            TestDemand.objects.filter(pk=form.id).delete()
        else:
            return json_response(error='该条提测申请不允许被删除！')

        return json_response(data='success')

    # 测试完成提交
    def patch(self, request):
        form, error = JsonParser(
            Argument('id', type=int, help='参数id不能为空'),
            Argument('test_case', type=str, help='测试报告不能为空'),
            Argument('test_report', type=str, help='测试用例不能为空')
        ).parse(request.body)
        if error is not None:
            return json_response(error=error)

        test_demand = TestDemand.objects.filter(pk=form.id).first()
        test_demand.test_case = form.test_case
        test_demand.test_report = form.test_report
        test_demand.save()

        work_flow = WorkFlow.objects.filter(test_demand=form.id).first()
        work_flow.status = Status.COMPLETE_TEST.value
        work_flow.updated_by = request.user
        work_flow.updated_at = human_datetime()
        work_flow.save()

        subject = f'【spug通知】（{test_demand.demand_name}）测试完成通知'
        message = f'（{test_demand.demand_name}）已经测试完成，请合代码部署到线上环境'
        recipient_list = work_flow.notify_name.split(",")
        file_names = [test_demand.test_case, test_demand.test_report]
        record_item = {
            'status': work_flow.status,
            'user': request.user,
            'demand': test_demand
        }
        Thread(target=send_email, args=(subject, message, recipient_list, file_names, record_item)).start()
        return json_response(data='success')


class WorkFlowView(View):

    # 指定测试/重新测试/上线/上线完成
    # status 是当前工单的执行状态 指定测试为1 重新测试为2 上线为3  上线完成为6
    def patch(self, request):
        form, error = JsonParser(
            Argument('id', type=int, help='参数id不能为空'),
            Argument('status', type=int, help='参数status不能为空'),
            Argument('tester_name', required=False),
            Argument('notify_name', required=False)
        ).parse(request.body)
        if error is not None:
            return json_response(error=error)

        work_flow = WorkFlow.objects.filter(test_demand=form.id).first()
        if not work_flow:
            return json_response(error='未找到指定对象')

        if form.status == Status.DELEGATE_TEST.value:
            work_flow.status = Status.TESTING.value
        elif form.status == Status.COMPLETE_TEST.value:
            # 待上线更新sql执行状态
            if work_flow.sql_exec_status != ExecuteStatus.NO_NEED_EXECUTE.value:
                work_flow.sql_exec_status = ExecuteStatus.PROD_WAITING.value
            work_flow.status = Status.UNDER_ONLINE.value
        elif form.status == Status.COMPLETE_ONLINE.value:
            if work_flow.sql_exec_status == ExecuteStatus.NO_NEED_EXECUTE.value:
                work_flow.is_sync = True
            work_flow.status = Status.SYNC_ENV.value
        else:
            work_flow.status = form.status

        work_flow.updated_by = request.user
        work_flow.updated_at = human_datetime()
        if form.tester_name:
            work_flow.tester_name = form.tester_name
            work_flow.notify_name = work_flow.developer_name + ',' + form.tester_name
        if form.notify_name:
            work_flow.notify_name = form.notify_name

        work_flow.save()

        # 指定测试人员发送邮件通知
        if form.status in [Status.DELEGATE_TEST.value, Status.COMPLETE_ONLINE.value]:
            test_demand = TestDemand.objects.filter(pk=form.id).first()
            if form.status == Status.DELEGATE_TEST.value:
                subject = f'【spug通知】（{test_demand.demand_name}）待测试'
                message = f'（{test_demand.demand_name}）待测试'
                file_names = None
            else:
                subject = f'【spug通知】（{test_demand.demand_name}）上线通知'
                message = f'（{test_demand.demand_name}）已经部署到线上环境，请验证'
                file_names = None

            recipient_list = work_flow.notify_name.split(",")
            record_item = {
                'status': form.status,
                'user': request.user,
                'demand': test_demand
            }
            Thread(target=send_email, args=(subject, message, recipient_list, file_names, record_item)).start()

        return json_response(data='success')

    # 运维上线申请
    def get(self, request):
        form, error = JsonParser(
            Argument('id', type=int, help='参数id不能为空'),
        ).parse(request.GET)
        if error is not None:
            return json_response(error=error)

        test_demand = TestDemand.objects.filter(pk=form.id).first()

        projects = DevelopProject.objects.filter(test_demand=form.id)
        del form.id
        deploy_request_id_set = set()
        for item in list(projects):
            # 已经同步好的申请不再发布
            if item.deploy_request_id:
                deploy_request_id_set.add(item.deploy_request_id)
                continue
            deploy = Deploy.objects.get(pk=item.deploy_id)
            if not deploy:
                return json_response(error='未找到指定应用')
            if deploy.extend == '2':
                return json_response(error='该应用不支持此操作')

            form.deploy_id = item.deploy_id
            form.host_ids = deploy.host_ids
            form.name = item.app_name + '_' + test_demand.demand_name
            form.status = '0' if deploy.is_audit else '1'
            form.spug_version = Repository.make_spug_version(item.deploy_id)
            # 获取最新发布版本
            branches, tags = fetch_versions(deploy)
            version = branches[item.branch_name][0]['id']
            form.version = f'{item.branch_name}#{version[:6]}'

            form.extra = json.dumps(['branch', item.branch_name, version])

            req = DeployRequest.objects.create(created_by=request.user, **form)
            item.deploy_request_id = req.id
            item.save()
            # 运维申请发送邮件
            is_required_notify = deploy.is_audit
            if is_required_notify:
                Thread(target=Helper.send_deploy_notify, args=(req, 'approve_req')).start()
        if deploy_request_id_set:
            return json_response(error='正在发布中，请勿重新发布！')
        return json_response(error=error)


# 定时任务 获取发布状态
def sync_deploy_request_status():
    # 获取需要同步的发布状态
    need_sync_workflow = WorkFlow.objects.select_related("test_demand").filter(status=Status.ONLINE.value,
                                                                               sql_exec_status__in=[
                                                                                   ExecuteStatus.NO_NEED_EXECUTE.value,
                                                                                   ExecuteStatus.PROD_FINISH.value,
                                                                                   ExecuteStatus.NO_NEED_EXECUTE.value])
    if not need_sync_workflow:
        return
    for item in list(need_sync_workflow):
        deploy_request_ids = list(item.test_demand.projects.values_list("deploy_request_id", flat=True))

        deploy_status_list = DeployRequest.objects.values_list('status', flat=True).filter(
            pk__in=deploy_request_ids)
        if deploy_status_list and set(deploy_status_list) == {'3'}:
            item.status = Status.COMPLETE_ONLINE.value
            item.save()
        # 通知测试 发送邮件
        item.test_demand


# 定时任务 通知需要同步环境的人
def notify_sync_test_env_databases():
    # 获取需要通知的提测申请
    need_sync_workflow = WorkFlow.objects.filter(status=Status.SYNC_ENV.value, is_sync=False)
    if not need_sync_workflow:
        return

    if need_sync_workflow:
        for workflow in list(need_sync_workflow):
            executes = list(workflow.orders.filter(sync_env='test'))
            sync_env = {item.db_name.split(sep='_')[-1] for item in executes}
            status = {item.status for item in executes}

            if settings.SYNC_ENV.difference(sync_env) or status != {SqlExecuteStatus.SUCCESS.value}:
                # 发送邮件提醒
                test_demand = workflow.test_demand
                subject = f'【spug通知】（{test_demand.demand_name}）同步测试环境通知'
                message = f'（{test_demand.demand_name}）还有脚本没有同步到测试环境，请前往同步'
                file_names = None

                recipient_list = workflow.notify_name.split(",")
                record_item = {
                    'status': Status.SYNC_ENV.value,
                    'user': User.objects.filter(username='admin').first(),
                    'demand': workflow.test_demand
                }
                Thread(target=send_email, args=(subject, message, recipient_list, file_names, record_item)).start()
