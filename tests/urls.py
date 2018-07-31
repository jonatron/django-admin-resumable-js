import django
from django.conf.urls import include, url
#from django.urls import path
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    url(r'^admin_resumable/', include('admin_resumable.urls')),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        (r'^media/(?P<path>.*)$', django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT})
    ]
