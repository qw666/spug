from django.conf import settings
from minio import Minio


MINIO_CLIENT = Minio(
    settings.MINIO_STORAGE_ENDPOINT,
    access_key=settings.MINIO_STORAGE_ACCESS_KEY,
    secret_key=settings.MINIO_STORAGE_SECRET_KEY,
    secure=False,
)