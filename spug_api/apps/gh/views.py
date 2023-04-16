from django.db import transaction
from django.shortcuts import render
from django.views import View

from apps.account.models import User
from apps.gh.models import TestDemand, WorkFlow, DevelopProject, DatabaseConfig
from libs import json_response, JsonParser, Argument, auth, human_datetime
import json


# Create your views here.

class TestView(View):

    def post(self, request):
        form, error = JsonParser(
            Argument('demand_name', help='请输入需求名称'),
            Argument('demand_link', help='请输入需求链接'),
            Argument('developer_name', type=list, help='请输入开发人员'),
            Argument('tester_name', type=list, help='请输入测试人员'),
            Argument('projects', type=list, help='请选择工程信息'),
            # Argument('databases', type=list, help='请选择工程信息'),
        ).parse(request.body)

        if error is not None:
            return json_response(error=error)

        form.developer_name = ','.join(str(item) for item in form.developer_name)
        form.tester_name = ','.join(str(item) for item in form.tester_name)
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
                                                    deploy=item.deploy_id,
                                                    branch_name=item.branch_name,
                                                    created_at=request.user
                                                    )
                                     for item in form.projects]

            DevelopProject.objects.bulk_create(batch_database_config)

            if form.databases is not None:
                batch_database_config = [DatabaseConfig(test_demand=test_demand_id,
                                                        db_type=item.db_type,
                                                        instance=item.instance,
                                                        db_name=item.db_name,
                                                        sql_type=item.sql_type,
                                                        sql_content=item.sql_content,
                                                        created_at=request.user
                                                        )
                                         for item in form.databases]
                DatabaseConfig.objects.bulk_create(batch_database_config)

        return json_response(data='success')
