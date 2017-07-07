from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property
from django.http import HttpResponse
from django.views.generic import View
from admin_resumable.files import ResumableFile
from admin_resumable.helpers import get_storage


class UploadView(View):
    # inspired by another fork https://github.com/fdemmer/django-admin-resumable-js

    @cached_property
    def params(self):
        return getattr(self.request, self.request.method)

    def model_field(self):
        ctype = ContentType.objects.get_for_id(self.params['content_type_id'])
        return ctype.model_class()._meta.get_field(self.params['field_name'])

    def post(self, request, *args, **kwargs):
        upload_to = self.model_field().orig_upload_to
        storage = get_storage(upload_to)
        chunk = request.FILES.get('file')
        r = ResumableFile(storage, request.POST)
        if not r.chunk_exists:
            r.process_chunk(chunk)
        if r.is_complete:
            actual_filename = storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(storage.url(actual_filename))
        return HttpResponse('chunk uploaded')

    def get(self, request, *args, **kwargs):
        upload_to = self.model_field().orig_upload_to
        storage = get_storage(upload_to)
        r = ResumableFile(storage, request.GET)
        if not r.chunk_exists:
            return HttpResponse('chunk not found', status=404)
        if r.is_complete:
            actual_filename = storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(storage.url(actual_filename))
        return HttpResponse('chunk exists')


admin_resumable = staff_member_required(UploadView.as_view())
