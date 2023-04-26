from datetime import datetime

from django.http import HttpResponseBadRequest, HttpResponse

from apps.gh.minio.utils import MINIO_CLIENT
from libs import json_response
from spug.overrides import MINIO_STORAGE_BUCKET_NAME

bucket_name = MINIO_STORAGE_BUCKET_NAME


# minio文件上传
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        prefix: str = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = prefix + file.name
        if not MINIO_CLIENT.bucket_exists(bucket_name):
            MINIO_CLIENT.make_bucket(bucket_name)
        MINIO_CLIENT.put_object(bucket_name, filename, file, length=file.size)
        return json_response(filename)
    else:
        return HttpResponseBadRequest


# minio文件下载
def download_file(request):
    file_name: str = request.GET['file_name']
    if file_name:
        object_data = MINIO_CLIENT.get_object(bucket_name, file_name)
        file_content = object_data.data
        # 将文件内容作为响应发送给客户端
        response = HttpResponse(file_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename={file_name}'.encode()
        return response
