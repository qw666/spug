from django.urls import path

from apps.gh.email.email import send_email_req

urlpatterns = [
    path('send_email/', send_email_req),
]
