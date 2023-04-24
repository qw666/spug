from django.urls import path

from apps.gh.email.email import send_email_req, send_deploy_email, start_send_webhook

urlpatterns = [
    path('send_email/', send_email_req),
    path('send_deploy_email/', send_deploy_email),
    path('start_send_webhook/', start_send_webhook),
]
