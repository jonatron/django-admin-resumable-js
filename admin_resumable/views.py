# -*- coding: utf-8 -*-
import logging

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views import View

from admin_resumable.files import ResumableFile
from admin_resumable.storage import resumable_default_storage

log = logging.getLogger(__name__)


@method_decorator(staff_member_required, name='dispatch')
class ResumableView(View):
    @cached_property
    def params(self):
        return getattr(self.request, self.request.method)

    @cached_property
    def model_field(self):
        """
        Determine the model field for the uploaded file/chunk using the
        'content_type_id' and 'field_name' request parameters.
        """
        ctype = ContentType.objects.get_for_id(self.params['content_type_id'])
        # noinspection PyProtectedMember
        return ctype.model_class()._meta.get_field(self.params['field_name'])

    @cached_property
    def storage(self):
        return resumable_default_storage

    @cached_property
    def resumable(self):
        return ResumableFile(self.storage, self.params)

    def post(self, request, *args, **kwargs):
        if not self.resumable.chunk_exists:
            chunk = request.FILES.get('file')
            self.resumable.process_chunk(chunk)

        if self.resumable.is_complete:
            log.debug('POST: is complete')
            return self.file_is_complete()

        return HttpResponse('chunk uploaded')

    def get(self, request, *args, **kwargs):
        if not self.resumable.chunk_exists:
            return HttpResponse('chunk not found', status=404)

        if self.resumable.is_complete:
            log.debug('GET: is complete')
            return self.file_is_complete()

        return HttpResponse('chunk exists')

    def file_is_complete(self, delete_chunks=True):
        # get filename incl upload_to and truncating to max_length
        filename = self.model_field.generate_filename(
            None, self.resumable.filename
        )

        log.debug('saving file...')
        actual_filename = self.storage.save(
            filename,
            self.resumable.file,
            max_length=self.model_field.max_length
        )
        log.debug('file saved (%s)', actual_filename)

        if delete_chunks:
            self.resumable.delete_chunks()
            log.debug('deleted chunks')

        return HttpResponse(actual_filename)

admin_resumable = ResumableView.as_view()
