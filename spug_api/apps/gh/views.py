from django.db import transaction
from django.views import View

from apps.gh.models import TestDemand, WorkFlow, DevelopProject, DatabaseConfig
from libs import json_response, JsonParser, Argument, auth
import json


# Create your views here.

class TestView(View):

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

        form.notify_name = form.developer_name + ',' + form.tester_name

        with transaction.atomic():

            test_demand_id = TestDemand.objects.create(demand_name=form.demand_name,
                                                       demand_link=form.demand_link,
                                                       created_by=request.user)

            WorkFlow.objects.create(test_demand=test_demand_id,
                                    developer_name=form.developer_name,
                                    tester_name=form.tester_name,
                                    notify_name=form.notify_name,
                                    created_by=request.user
                                    )

            batch_database_config = [DevelopProject(test_demand=test_demand_id,
                                                    deploy_id=item.get('deploy_id'),
                                                    branch_name=item.get('branch_name'),
                                                    created_by=request.user
                                                    )
                                     for item in form.projects]

            DevelopProject.objects.bulk_create(batch_database_config)

            if form.databases is not None:
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

        # TODO 提交测试申请 发生邮件
        return json_response(data='success')
