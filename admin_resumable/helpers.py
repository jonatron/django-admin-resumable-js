from django.core.files.storage import get_storage_class

from admin_resumable.conf import persistent_storage_class_name, chunk_storage_class_name


def get_chunk_storage(*args, **kwargs):
    """
    Returns storage class specified in settings as ADMIN_RESUMABLE_CHUNK_STORAGE.
    Defaults to django.core.files.storage.FileSystemStorage.
    Chunk storage should be highly available for the server as saved chunks must be copied by the server
    for saving merged version in persistent storage.
    """
    storage_class = get_storage_class(chunk_storage_class_name)
    return storage_class(*args, **kwargs)


def get_persistent_storage(*args, **kwargs):
    """
    Returns storage class specified in settings as ADMIN_RESUMABLE_STORAGE
    or DEFAULT_FILE_STORAGE if the former is not found.

    Defaults to django.core.files.storage.FileSystemStorage.
    """
    storage_class = get_storage_class(persistent_storage_class_name)
    return storage_class(*args, **kwargs)
