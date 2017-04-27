from __future__ import absolute_import


from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from admin_resumable.storage import get_storage
from admin_resumable.utils import get_model_field
from .files import ResumableFile



@staff_member_required
def admin_resumable(request):
    field = get_model_field(request)
    storage = get_storage()

    if request.method == 'POST':
        chunk = request.FILES.get('file')
        r = ResumableFile(storage, request.POST)
        if not r.chunk_exists:
            r.process_chunk(chunk)
        if r.is_complete:
            actual_filename = storage.save(
                field.generate_filename(None, r.filename),
                r.file, max_length=field.max_length
            )
            r.delete_chunks()
            return HttpResponse(actual_filename)
        return HttpResponse('chunk uploaded')

    elif request.method == 'GET':
        r = ResumableFile(storage, request.GET)
        if not r.chunk_exists:
            return HttpResponse('chunk not found', status=404)
        if r.is_complete:
            actual_filename = storage.save(
                field.generate_filename(None, r.filename),
                r.file, max_length=field.max_length
            )
            r.delete_chunks()
            return HttpResponse(actual_filename)
        return HttpResponse('chunk exists')
