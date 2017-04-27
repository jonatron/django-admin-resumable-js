from django.conf import settings
from django.core.files.storage import get_storage_class

from admin_resumable.conf import ADMIN_RESUMABLE_STORAGE


def get_storage():
    """
    Looks at the ADMIN_RESUMABLE_STORAGE setting and returns
    an instance of the storage class specified.

    Defaults to django.core.files.storage.FileSystemStorage.

    Any custom storage class used here must either be a subclass of
    django.core.files.storage.FileSystemStorage, or accept a location
    init parameter.
    """
    base_url = settings.MEDIA_URL
    location = settings.MEDIA_ROOT

    #subdir = getattr(settings, 'ADMIN_RESUMABLE_SUBDIR', None)
    #if subdir is not None:
    #    base_url = settings.MEDIA_URL + subdir
    #    location = os.path.join(settings.MEDIA_ROOT, subdir)
    #    ensure_dir(location)

    storage_class = get_storage_class(ADMIN_RESUMABLE_STORAGE)
    return storage_class(location=location, base_url=base_url)
