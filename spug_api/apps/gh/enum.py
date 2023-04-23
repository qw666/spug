from enum import Enum


# 角色枚举类 1 开发 ，2 测试
class RoleType(Enum):
    DEV = 1
    TEST = 2


# 提测申请业务状态枚举类
class Status(Enum):
    # 待测试
    UNDER_TEST = 0
    # 指定测试
    DELEGATE_TEST = 1
    # 测试中
    TESTING = 2
    # 测试完成
    COMPLETE_TEST = 3
    # 待上线
    UNDER_ONLINE = 4
    # 上线中
    ONLINE = 5
    # 上线完成
    COMPLETE_ONLINE = 6


# 提测申请sql执行状态枚举类
class ExecuteStatus(Enum):
    # 测试环境待执行
    TEST_WAITING = 0
    # 测试环境执行中
    TEST_EXECUTING = 1
    # 测试环境已执行
    TEST_FINISH = 2
    # 测试环境执行失败
    TEST_EXCEPTION = 3
    # 线上环境待执行
    PROD_WAITING = 4
    # 线上环境执行中
    PROD_EXECUTING = 5
    # 线上环境已执行
    PROD_FINISH = 6
    # 线上环境执行失败
    PROD_EXCEPTION = 7


# sql执行状态枚举类
class SqlExecuteStatus(Enum):
    # 执行中
    EXECUTING = 0
    # 成功
    SUCCESS = 1
    # 失败
    FAILURE = 2


# archery sql 审核平台的SQL工单枚举类
class OrderStatus(Enum):
    # 已正常结束
    WORKFLOW_FINISH = 'workflow_finish'
    # 人工终止流程
    WORKFLOW_ABORT = 'workflow_abort'
    # 等待审核人审核
    WORKFLOW_MAN_REVIEWING = 'workflow_manreviewing'
    # 测试完成
    WORKFLOW_REVIEW_PASS = 'workflow_review_pass'
    # 定时执行
    WORKFLOW_TIMING_TASK = 'workflow_timingtask'
    # 排队中
    WORKFLOW_QUEUING = 'workflow_queuing'
    # 执行中
    WORKFLOW_EXECUTING = 'workflow_executing'
    # 自动审核不通过
    WORKFLOW_AUTO_REVIEW_WRONG = 'workflow_autoreviewwrong'
    # 执行有异常
    WORKFLOW_EXCEPTION = 'workflow_exception'


# 提测申请同步测试状态枚举类
class SyncStatus(Enum):
    # 待同步
    WAITING_SYNCHRONIZE = 0
    # 同步中
    SYNCHRONIZING = 1
    # 同步完成
    SYNCHRONIZE_FINISH = 2
    # 同步失败
    SYNCHRONIZE_EXCEPTION = 3
