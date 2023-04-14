from django.db import models

from apps.app.models import Deploy
from libs import human_datetime
from apps.account.models import User


class TestDemand(models.Model):
    # 需求名称
    demand_name = models.CharField(max_length=50)
    # 需求链接
    demand_link = models.CharField(max_length=300)
    # TODO 增加文件上传和下载
    # 测试用例
    # test_case = models.CharField(max_length=100)
    # 测试报告
    # test_report = models.FilePathField(max_length=100)
    # 申请人
    created_at = models.FilePathField(max_length=20, default=human_datetime)
    # 申请时间
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    # 提测的需求信息表 test_demand
    class Meta:
        db_table = 'test_demand'
        ordering = ('-id',)


class WorkFlow(models.Model):
    STATUS = (
        (0, '待测试'),
        (1, '测试中'),
        (2, '测试完成'),
        (3, '待上线'),
        (4, '上线中'),
        (5, '上线完成')
    )

    SQL_EXEC_STATUS = (
        (0, '测试环境待执行'),
        (1, '测试环境执行中'),
        (2, '测试环境已执行'),
        (3, '测试环境执行失败'),
        (4, '线上环境待执行'),
        (5, '线上环境执行中'),
        (6, '线上环境已执行'),
        (7, '线上环境执行失败'),
        (8, '测试环境待同步'),
        (9, '测试环境同步中'),
        (10, '测试环境同步成功'),
        (11, '测试环境同步失败'),
    )

    # 需求ID
    test_demand = models.OneToOneField(TestDemand, on_delete=models.CASCADE)
    # 是否同步测试环境
    is_sync = models.BooleanField(default=False)
    # 开发人员
    developer_name = models.CharField(max_length=100)
    # 测试人员
    tester_name = models.CharField(max_length=100)
    # 通知人员
    notify_name = models.CharField(max_length=100, null=True)
    # 测试状态
    status = models.SmallIntegerField(choices=STATUS, default=0)
    # 测试状态
    sql_exec_status = models.SmallIntegerField(choices=SQL_EXEC_STATUS, default=0)
    # 操作人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')
    # 操作时间
    created_at = models.CharField(max_length=20, default=human_datetime)

    # 提测的工作流信息表 work_flow
    class Meta:
        db_table = 'work_flow'
        ordering = ('-id',)


class DevelopProject(models.Model):
    # 需求ID
    test_demand = models.ForeignKey(TestDemand, on_delete=models.CASCADE)
    # 部署的工程id 按94环境处理
    deploy_id = models.ForeignKey(Deploy, on_delete=models.CASCADE)
    # 分支信息
    branch_name = models.CharField(max_length=100)
    # 申请时间
    created_at = models.FilePathField(max_length=20, default=human_datetime)
    # 申请人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    # 工程信息表 develop_project
    class Meta:
        db_table = 'deploy_project'
        ordering = ('-id',)


class DatabaseConfig(models.Model):

    SQL_TYPE = (
        (1, 'DDL'),
        (2, 'DML'),
    )
    # 需求ID
    test_demand = models.ForeignKey(TestDemand, on_delete=models.CASCADE)
    # 数据库类型 mysql pgsql
    db_type = models.CharField(max_length=50)
    # 数据库名称
    db_name = models.CharField(max_length=50)
    # 数据库实例
    instance = models.SmallIntegerField()
    # sql类型
    sql_type = models.SmallIntegerField(choices=SQL_TYPE)
    # sql内容
    sql_content = models.CharField(max_length=1000)
    # 申请时间
    created_at = models.FilePathField(max_length=20, default=human_datetime)
    # 申请人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    # 数据库sql配置表 database_config
    class Meta:
        db_table = 'database_config'
        ordering = ('-id',)
