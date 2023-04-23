from django.urls import path

from apps.gh.minio.minio import *

urlpatterns = [
    path('fileupload/', upload_file),
    path('download/', download_file),
]