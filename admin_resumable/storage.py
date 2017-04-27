# -*- coding: utf-8 -*-
from django.core.files.storage import get_storage_class
from django.utils.functional import LazyObject

from admin_resumable import conf


class ResumableDefaultStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(conf.ADMIN_RESUMABLE_STORAGE)()


resumable_default_storage = ResumableDefaultStorage()
