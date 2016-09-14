from django.conf import settings
from django.db import models

from admin_resumable.fields import ModelAdminResumableFileField


# Stolen from the README
class Foo(models.Model):
    bar = models.CharField(max_length=200)
    foo = ModelAdminResumableFileField()
    bat = ModelAdminResumableFileField(upload_to=settings.MEDIA_ROOT + '/upto/')
