from django.db import models

from libs import human_datetime, ModelMixin
from apps.account.models import User


class TestDemand(models.Model, ModelMixin):
    # 需求名称
    demand_name = models.CharField(max_length=50)
    # 需求链接
    demand_link = models.CharField(max_length=300)
    # 测试用例
    test_case = models.CharField(max_length=100)
    # 测试报告
    test_report = models.CharField(max_length=100)
    # 申请时间
    created_at = models.CharField(max_length=20, default=human_datetime)
    # 申请人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    # 提测的需求信息表 test_demand
    class Meta:
        db_table = 'test_demand'
        ordering = ('-id',)


class WorkFlow(models.Model, ModelMixin):
    STATUS = (
        (0, '待测试'),
        (1, '指定测试'),
        (2, '测试中'),
        (3, '测试完成'),
        (4, '待上线'),
        (5, '上线中'),
        (6, '上线完成')
    )

    SQL_EXEC_STATUS = (
        (0, '测试环境待执行'),
        (1, '测试环境执行中'),
        (2, '测试环境已执行'),
        (3, '测试环境执行失败'),
        (4, '线上环境待执行'),
        (5, '线上环境执行中'),
        (6, '线上环境已执行'),
        (7, '线上环境执行失败')
    )

    SYNC_STATUS = (
        (0, '待同步'),
        (1, '同步中'),
        (2, '同步完成'),
        (3, '同步失败')
    )

    # 需求ID
    test_demand = models.OneToOneField(TestDemand, on_delete=models.CASCADE)
    # 是否同步测试环境
    is_sync = models.SmallIntegerField(choices=SYNC_STATUS, default=0)
    # 开发人员
    developer_name = models.CharField(max_length=100)
    # 测试人员
    tester_name = models.CharField(max_length=100)
    # 通知人员
    notify_name = models.CharField(max_length=100, null=True)
    # 测试状态
    status = models.SmallIntegerField(choices=STATUS, default=0)
    # sql执行状态
    sql_exec_status = models.SmallIntegerField(choices=SQL_EXEC_STATUS, default=0)
    # 更新人
    updated_by = models.ForeignKey(User, models.PROTECT, related_name='+')
    # 更新时间
    updated_at = models.CharField(max_length=20, default=human_datetime)

    # 提测的工作流信息表 work_flow
    class Meta:
        db_table = 'work_flow'
        ordering = ('-id',)


class DevelopProject(models.Model, ModelMixin):
    # 需求ID
    test_demand = models.ForeignKey(TestDemand, on_delete=models.CASCADE, related_name='projects')
    # 部署的工程id 按94环境处理
    deploy_id = models.SmallIntegerField()
    # 工程名称
    app_name = models.CharField(max_length=100)
    # 分支信息
    branch_name = models.CharField(max_length=100)
    # 申请时间
    created_at = models.CharField(max_length=20, default=human_datetime)
    # 申请人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    # 工程信息表 develop_project
    class Meta:
        db_table = 'deploy_project'
        ordering = ('-id',)


class DatabaseConfig(models.Model, ModelMixin):
    SQL_TYPE = (
        (1, 'DDL'),
        (2, 'DML'),
    )
    # 需求ID
    test_demand = models.ForeignKey(TestDemand, on_delete=models.CASCADE, related_name='databases')
    # 数据库类型 mysql pgsql
    db_type = models.CharField(max_length=50)
    # 数据库名称
    db_name = models.CharField(max_length=50)
    # 数据库所属组
    group_id = models.SmallIntegerField()
    # 数据库实例
    instance = models.SmallIntegerField()
    # sql类型
    sql_type = models.SmallIntegerField(choices=SQL_TYPE)
    # sql内容
    sql_content = models.CharField(max_length=1000)
    # 申请时间
    created_at = models.CharField(max_length=20, default=human_datetime)
    # 申请人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    # 数据库sql配置表 database_config
    class Meta:
        db_table = 'database_config'
        ordering = ('-id',)


class SqlExecute(models.Model, ModelMixin):
    SQL_TYPE = (
        (1, 'DDL'),
        (2, 'DML'),
    )
    SQL_EXEC_STATUS = (
        (0, '执行中'),
        (1, '执行成功'),
        (2, '执行失败')
    )

    # 需求ID
    workflow = models.ForeignKey(WorkFlow, on_delete=models.CASCADE, related_name='orders')
    # SQL审核平台的工单ID
    order_id = models.IntegerField()
    # 需求名称
    demand_name = models.CharField(max_length=50)
    # 需求链接
    demand_link = models.CharField(max_length=300)
    # sql类型
    sql_type = models.SmallIntegerField(choices=SQL_TYPE)
    # 执行环境 test/prod
    env = models.CharField(max_length=5)
    # 数据库所属组
    group_id = models.SmallIntegerField()
    # 数据库实例
    instance = models.SmallIntegerField()
    # 数据库类型 mysql pgsql
    db_type = models.CharField(max_length=50)
    # 数据库名称
    db_name = models.CharField(max_length=50)
    # 是否备份
    is_backup = models.BooleanField(default=True)
    # 执行状态
    status = models.SmallIntegerField(choices=SQL_EXEC_STATUS, default=0)
    # sql内容
    sql_content = models.CharField(max_length=1000)
    # 申请时间
    created_at = models.CharField(max_length=20, default=human_datetime)
    # 申请人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    # 数据库sql执行表 sql_execute
    class Meta:
        db_table = 'sql_execute'
        ordering = ('-id',)


class UserExtend(models.Model, ModelMixin):
    # 姓名
    nickname = models.CharField(max_length=100)
    # 邮箱
    email = models.CharField(max_length=100)

    class Meta:
        db_table = 'user_extend'
        ordering = ('-id',)


class SendRecord(models.Model, ModelMixin):
    # 项目id
    test_demand = models.ForeignKey(TestDemand, on_delete=models.CASCADE, related_name='record')
    # 发件人
    sender = models.CharField(verbose_name='发件人', max_length=500)
    # 收件人
    receiver = models.CharField(verbose_name='收件人', max_length=500)
    # 发送内容
    content = models.CharField(verbose_name='发送内容', max_length=1000)
    # 项目阶段
    project_status = models.SmallIntegerField()
    # 发送状态 1成功 2失败
    send_status = models.SmallIntegerField(verbose_name='发送状态 1成功 2失败', default=1)
    # 创建时间
    created_at = models.CharField(max_length=20, default=human_datetime)
    # 创建人
    created_by = models.ForeignKey(User, models.PROTECT, related_name='+')

    class Meta:
        db_table = 'send_record'
        ordering = ('-id',)
