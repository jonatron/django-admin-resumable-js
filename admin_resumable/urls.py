from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^admin_resumable/$', 'admin_resumable.views.admin_resumable', name='admin_resumable'),
)
