import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import get_storage_class
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

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
    return storage_class(location=location, base_url=url_path)


def get_upload_to(request):
    if request.method == 'POST':
        ct_id = request.POST['content_type_id']
        field_name = request.POST['field_name']
    else:
        ct_id = request.GET['content_type_id']
        field_name = request.GET['field_name']

    ct = ContentType.objects.get_for_id(ct_id)
    model_cls = ct.model_class()
    field = model_cls._meta.get_field(field_name)
    return field.orig_upload_to


@staff_member_required
def admin_resumable(request):
    upload_to = get_upload_to(request)
    storage = get_storage(upload_to)
    if request.method == 'POST':
        chunk = request.FILES.get('file')
        r = ResumableFile(storage, request.POST)
        if not r.chunk_exists:
            r.process_chunk(chunk)
        if r.is_complete:
            actual_filename = storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(storage.url(actual_filename))
        return HttpResponse('chunk uploaded')
    elif request.method == 'GET':
        r = ResumableFile(storage, request.GET)
        if not r.chunk_exists:
            return HttpResponse('chunk not found', status=404)
        if r.is_complete:
            actual_filename = storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(storage.url(actual_filename))
        return HttpResponse('chunk exists')
