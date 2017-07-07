from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse

from admin_resumable.files import ResumableFile
from admin_resumable.helpers import get_upload_to, get_storage


@staff_member_required
def admin_resumable(request):
    upload_to = get_upload_to(request)      # basically get_directory_name for proper content type and its field
    storage = get_storage(upload_to)        # storage class with proper parameters
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
