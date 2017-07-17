import datetime

import posixpath
from django.core.files.storage import get_storage_class

from django.conf import settings
from django.utils.encoding import force_text, force_str


class ResumableStorage(object):

    def __init__(self):
        self.persistent_storage_class_name = getattr(settings, 'ADMIN_RESUMABLE_STORAGE', None) or \
                                        getattr(settings, 'DEFAULT_FILE_STORAGE',
                                                'django.core.files.storage.FileSystemStorage')

        self.chunk_storage_class_name = getattr(
            settings,
            'ADMIN_RESUMABLE_CHUNK_STORAGE',
            'django.core.files.storage.FileSystemStorage'
        )

    def get_chunk_storage(self, *args, **kwargs):
        """
        Returns storage class specified in settings as ADMIN_RESUMABLE_CHUNK_STORAGE.
        Defaults to django.core.files.storage.FileSystemStorage.
        Chunk storage should be highly available for the server as saved chunks must be copied by the server
        for saving merged version in persistent storage.
        """
        storage_class = get_storage_class(self.chunk_storage_class_name)
        return storage_class(*args, **kwargs)

    def get_persistent_storage(self, *args, **kwargs):
        """
        Returns storage class specified in settings as ADMIN_RESUMABLE_STORAGE
        or DEFAULT_FILE_STORAGE if the former is not found.

        Defaults to django.core.files.storage.FileSystemStorage.
        """
        storage_class = get_storage_class(self.persistent_storage_class_name)
        return storage_class(*args, **kwargs)

    def full_filename(self, filename, upload_to):
        dirname = force_text(datetime.datetime.now().strftime(force_str(upload_to)))
        filename = posixpath.join(dirname, filename)
        return self.get_persistent_storage().generate_filename(filename)
