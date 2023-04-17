from django.urls import path

from apps.gh.app.app import list_apps, get_versions

urlpatterns = [
    path('listApps/', list_apps),
    path('deploy/<int:d_id>/versions/', get_versions),
]