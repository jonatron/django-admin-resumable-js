from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from distutils.version import StrictVersion
import django


if StrictVersion(django.get_version()) < StrictVersion('1.7'):
    admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin_resumable/', include('admin_resumable.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}))
