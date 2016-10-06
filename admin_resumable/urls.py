from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^admin_resumable/$', views.admin_resumable, name='admin_resumable'),
]
