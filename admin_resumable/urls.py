from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/$', views.admin_resumable, name='admin_resumable'),
]
