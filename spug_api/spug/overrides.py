DEBUG = False

DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'spug',  # 替换为自己的数据库名，请预先创建好编码为utf8mb4的数据库
        'USER': 'spug_user',  # 数据库用户名
        'PASSWORD': '95vQkU88E_tfdS',  # 数据库密码
        'HOST': '10.188.15.56',  # 数据库地址
        'PORT': '3402',  # 数据库地址
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_TRANS_TABLES',
            # 'unix_socket': '/opt/mysql/mysql.sock' # 如果是本机数据库,且不是默认安装的Mysql,需要指定Mysql的socket文件路径
        }
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:85_wdV60pvRCAY@10.188.15.56:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://:85_wdV60pvRCAY@10.188.15.56:6379/0"],
            "capacity": 1000,
            "expiry": 120,
        },
    },
}

# minio相关配置
MINIO_STORAGE_ENDPOINT = '10.188.15.56:9765'
MINIO_STORAGE_ACCESS_KEY = 'root'
MINIO_STORAGE_SECRET_KEY = 'aUxE_MeRmjrzC4'
MINIO_STORAGE_BUCKET_NAME = 'spug-file-bucket'

# 126邮箱相关配置
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.126.com'
# EMAIL_PORT = 25
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'gohightest@126.com'
# EMAIL_HOST_PASSWORD = 'RGWDYWZKNPGLEVXV'
# 腾讯企业邮箱相关配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False  # 是否使用TLS安全传输协议
EMAIL_USE_SSL = True  # 是否使用SSL加密，qq企业邮箱要求使用
EMAIL_HOST_USER = 'chenqi@gohigh.com.cn'
EMAIL_HOST_PASSWORD = 'Qichen8906'
DEFAULT_FROM_EMAIL = 'chenqi@gohigh.com.cn'
EMAIL_USE_LOCALTIME = True

# Archery sql 审核平台相关配置
DATABASE_TEST_ENV = 'test'
DATABASE_PROD_ENV = 'prod'

ARCHERY_SQL_PASSWORD = 'gohigh@123'
GET_AUTH_TOKEN_URL = 'http://10.188.15.53:9123/api/auth/token/'
GET_INSTANCE_URL = 'http://10.188.15.53:9123/api/v1/instance/'
GET_RESOURCE_URL = 'http://10.188.15.53:9123/api/v1/instance/resource/'
CHECK_SQL_URL = 'http://10.188.15.53:9123/api/v1/workflow/sqlcheck/'
WORKFLOW_SUBMIT_URL = 'http://10.188.15.53:9123/api/v1/workflow/'
WORKFLOW_AUDIT_URL = 'http://10.188.15.53:9123/api/v1/workflow/audit/'
WORKFLOW_EXECUTE_URL = 'http://10.188.15.53:9123/api/v1/workflow/execute/'
GET_WORKFLOW_RESULT_URL = 'http://10.188.15.53:9123/api/v1/workflow/?page=1&size=10'

# 提测申请相关配置
VIEW_ENV = ['test230', 'test231', 'test232', 'test233']
SYNC_ENV = {'test230', 'test231', 'test232'}
IGNORE_SYNC_ENV = ['test233']
