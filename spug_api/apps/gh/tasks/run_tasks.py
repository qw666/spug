from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job

from apps.gh.archery.archery import sync_workflow_sql_execute
from apps.gh.views import sync_deploy_status

# 1.实例化调度器
scheduler = BackgroundScheduler()

# 2.调度器使用DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), "default")

try:
    # 3.设置定时任务，选择方式为interval，时间间隔为10s
    # 另一种方式为每天固定时间执行任务，对应代码为：
    # @register_job(scheduler, 'cron', hour='9', minute='30', second='10',id='task_time')
    @register_job(scheduler, "interval", minutes=1, replace_existing=True)
    def sync_archery_sql_execute():
        # 定时任务获取sql执行结果
        try:
            sync_workflow_sql_execute()
        except Exception as error:
            print(error)


    @register_job(scheduler, "interval", seconds=15, replace_existing=True)
    def sync_deploy_request_status():
        # 定时任务获取发布申请的发布状态
        try:
            sync_deploy_status()
        except Exception as error:
            print(error)


    # 4.注册定时任务
    # register_events(scheduler)  # 新版本已经不需要这一步了

    # 5.开启定时任务
    scheduler.start()
except Exception as e:
    print(e)
    # 有错误就停止定时器
    scheduler.shutdown()
