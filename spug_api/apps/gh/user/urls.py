from django.urls import path

from apps.gh.user.user import *

urlpatterns = [
    path('listUsers/', list_users),
]