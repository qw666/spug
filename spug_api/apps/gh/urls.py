# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the AGPL-3.0 License.
from django.urls import path

from apps.gh.views import TestView, WorkFlowView, TestReportView

urlpatterns = [
    path('test/', TestView.as_view()),
    path('workflow/', WorkFlowView.as_view()),
    path('test_report/', TestReportView.as_view()),

]
