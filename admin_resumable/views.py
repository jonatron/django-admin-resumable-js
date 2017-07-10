import datetime

import posixpath
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.http import HttpResponse
from django.utils.encoding import force_text, force_str
from django.utils.functional import cached_property
from django.views.generic import View
from admin_resumable.files import ResumableFile
from admin_resumable.helpers import get_persistent_storage, get_chunk_storage


class UploadView(View):
    # inspired by another fork https://github.com/fdemmer/django-admin-resumable-js

    @cached_property
    def request_data(self):
        return getattr(self.request, self.request.method)

    @cached_property
    def model_upload_field(self):
        content_type = ContentType.objects.get_for_id(self.request_data['content_type_id'])
        return content_type.model_class()._meta.get_field(self.request_data['field_name'])

    @property
    def _upload_to(self):
        return self.model_upload_field.upload_to

    def get_chunk_storage(self):
        return get_chunk_storage(
            # self._get_upload_to()
        )

    def get_persistent_storage(self):
        return get_persistent_storage(
            # self._get_upload_to()
        )

    def generate_filename(self, storage, filename):
        dirname = force_text(datetime.datetime.now().strftime(force_str(self._upload_to)))
        filename = posixpath.join(dirname, filename)
        return storage.generate_filename(filename)

    def post(self, request, *args, **kwargs):
        persistent_storage = self.get_persistent_storage()
        chunk_storage = self.get_chunk_storage()
        chunk = request.FILES.get('file')
        r = ResumableFile(chunk_storage, request.POST)
        if not r.chunk_exists:
            r.process_chunk(chunk)
        if r.is_complete:
            filename = self.generate_filename(persistent_storage, r.filename)
            actual_filename = persistent_storage.save(filename, File(r.file))
            r.delete_chunks()
            return HttpResponse(persistent_storage.url(actual_filename))
        return HttpResponse('chunk uploaded')

    def get(self, request, *args, **kwargs):
        persistent_storage = self.get_persistent_storage()
        chunk_storage = self.get_chunk_storage()
        r = ResumableFile(chunk_storage, request.GET)
        if not r.chunk_exists:
            return HttpResponse('chunk not found', status=404)
        if r.is_complete:
            filename = self.generate_filename(persistent_storage, r.filename)
            actual_filename = persistent_storage.save(filename, File(r.file))
            r.delete_chunks()
            return HttpResponse(persistent_storage.url(actual_filename))
        return HttpResponse('chunk exists')


admin_resumable = staff_member_required(UploadView.as_view())
