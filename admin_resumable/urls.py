# -*- coding: utf-8 -*-
from django.conf.urls import url

from admin_resumable.views import ResumableView

urlpatterns = [
    url(r'^upload/$', ResumableView.as_view(), name='admin_resumable'),
]
