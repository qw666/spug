# Author: Wang Cen
# Date: 2023/4/16 16:56
from django.urls import path

from apps.gh.archery.archery import get_instance, get_resource, check_sql, execute_sql, SyncView

urlpatterns = [
    path('instance', get_instance),
    path('resource', get_resource),
    path('check', check_sql),
    path('execute', execute_sql),
    path('sync', SyncView.as_view()),
]
