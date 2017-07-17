from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View
from admin_resumable.files import ResumableFile


class UploadView(View):
    # inspired by another fork https://github.com/fdemmer/django-admin-resumable-js

    @cached_property
    def request_data(self):
        return getattr(self.request, self.request.method)

    @cached_property
    def model_upload_field(self):
        content_type = ContentType.objects.get_for_id(self.request_data['content_type_id'])
        return content_type.model_class()._meta.get_field(self.request_data['field_name'])

    def post(self, request, *args, **kwargs):
        chunk = request.FILES.get('file')
        r = ResumableFile(self.model_upload_field, request.POST)
        if not r.chunk_exists:
            r.process_chunk(chunk)
        if r.is_complete:
            return HttpResponse(r.collect())
        return HttpResponse('chunk uploaded')

    def get(self, request, *args, **kwargs):
        r = ResumableFile(self.model_upload_field, request.GET)
        if not r.chunk_exists:
            return HttpResponse('chunk not found', status=404)
        if r.is_complete:
            return HttpResponse(r.collect())
        return HttpResponse('chunk exists')


admin_resumable = staff_member_required(UploadView.as_view())
