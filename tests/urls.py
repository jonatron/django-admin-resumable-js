import django
from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    url(r'^admin_resumable/', include('admin_resumable.urls')),
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        path(r'^media/(?P<path>.*)$', django.views.static.serve,
             kwargs={'document_root': settings.MEDIA_ROOT})
    ]
