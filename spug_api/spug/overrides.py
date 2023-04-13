# Database
DATABASES = {
    'default': {
        'ATOMIC_REQUESTS': True,
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'spug',  # 替换为自己的数据库名，请预先创建好编码为utf8mb4的数据库
        'USER': 'root',  # 数据库用户名
        'PASSWORD': '96vQkU88E_tfdS',  # 数据库密码
        'HOST': '10.188.15.192',  # 数据库地址
        'PORT': '3402',
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
        "LOCATION": "redis://10.188.15.180:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "85_wdV60pvRCAY"
        }
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://:85_wdV60pvRCAY@10.188.15.180:6379/4"],
            "capacity": 1000,
            "expiry": 120,
        },
    },
}

