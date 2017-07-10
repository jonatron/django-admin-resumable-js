from django.conf import settings


persistent_storage_class_name = getattr(settings, 'ADMIN_RESUMABLE_STORAGE', None) or \
                                getattr(settings, 'DEFAULT_FILE_STORAGE', 'django.core.files.storage.FileSystemStorage')

chunk_storage_class_name = getattr(
    settings,
    'ADMIN_RESUMABLE_CHUNK_STORAGE',
    'django.core.files.storage.FileSystemStorage'
)