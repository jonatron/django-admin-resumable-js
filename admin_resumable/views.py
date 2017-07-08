import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import get_storage_class
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View

from admin_resumable.files import ResumableFile


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def get_chunks_subdir():
    return getattr(settings, 'ADMIN_RESUMABLE_SUBDIR', 'admin_uploaded/')


def get_chunks_dir():
    chunks_subdir = get_chunks_subdir()
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root:
        raise ImproperlyConfigured(
            'You must set settings.MEDIA_ROOT')
    chunks_dir = os.path.join(media_root, chunks_subdir)
    ensure_dir(chunks_dir)
    return chunks_dir


def get_storage(upload_to):
    """
    Looks at the ADMIN_RESUMABLE_STORAGE setting and returns
    an instance of the storage class specified.

    Defaults to django.core.files.storage.FileSystemStorage.

    Any custom storage class used here must either be a subclass of
    django.core.files.storage.FileSystemStorage, or accept a location
    init parameter.
    """
    if upload_to:
        location = os.path.join(settings.MEDIA_ROOT, upload_to)
        url_path = os.path.join(settings.MEDIA_URL, upload_to)
        ensure_dir(location)
    else:
        url_path = os.path.join(settings.MEDIA_URL, get_chunks_subdir())
        location = get_chunks_dir()
    storage_class_name = getattr(
        settings,
        'ADMIN_RESUMABLE_STORAGE',
        'django.core.files.storage.FileSystemStorage'
    )
    storage_class = get_storage_class(storage_class_name)
    if storage_class_name == 'django.core.files.storage.FileSystemStorage':
        storage = storage_class(location=location, base_url=url_path)
    else:
        storage = storage_class()
    return storage


class UploadView(View):

    @cached_property
    def request_data(self):
        return getattr(self.request, self.request.method)

    def model_upload_field(self):
        content_type_id = self.request_data['content_type_id']
        field_name = self.request_data['field_name']
        content_type = ContentType.objects.get_for_id(content_type_id)
        model_class = content_type.model_class()
        return model_class._meta.get_field(field_name)

    def post(self, request, *args, **kwargs):
        upload_to = self.model_upload_field().orig_upload_to
        persistent_storage = get_storage(upload_to)
        chunk_storage = get_storage_class('django.core.files.storage.FileSystemStorage')(
            location=os.path.join(settings.MEDIA_ROOT, upload_to),
            base_url=os.path.join(settings.MEDIA_URL, upload_to),
        )
        chunk = request.FILES.get('file')
        r = ResumableFile(chunk_storage, request.POST)
        if not r.chunk_exists:
            r.process_chunk(chunk)
        if r.is_complete:
            actual_filename = persistent_storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(persistent_storage.url(actual_filename))
        return HttpResponse('chunk uploaded')

    def get(self, request, *args, **kwargs):
        upload_to = self.model_upload_field().orig_upload_to
        persistent_storage = get_storage(upload_to)
        chunk_storage = get_storage_class('django.core.files.storage.FileSystemStorage')(
            location=os.path.join(settings.MEDIA_ROOT, upload_to),
            base_url=os.path.join(settings.MEDIA_URL, upload_to),
        )
        r = ResumableFile(chunk_storage, request.GET)
        if not r.chunk_exists:
            return HttpResponse('chunk not found', status=404)
        if r.is_complete:
            actual_filename = persistent_storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(persistent_storage.url(actual_filename))
        return HttpResponse('chunk exists')


admin_resumable = staff_member_required(UploadView.as_view())
