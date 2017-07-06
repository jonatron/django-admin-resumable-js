import os

from django.forms.widgets import FileInput
from django.forms import forms
from django.db import models
from django.templatetags.static import static
from django.template import loader
from django.forms.fields import FileField
from django.forms.widgets import CheckboxInput
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext_lazy
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from .views import get_storage


def get_upload_to(ct_id, field_name):
    ct = ContentType.objects.get_for_id(ct_id)
    model_cls = ct.model_class()
    field = model_cls._meta.get_field(field_name)
    return field.orig_upload_to


class ResumableWidget(FileInput):
    template_name = 'admin_resumable/file_input.html'
    clear_checkbox_label = ugettext_lazy('Clear')

    def render(self, name, value, attrs=None, **kwargs):
        upload_to = get_upload_to(
            self.attrs['content_type_id'], self.attrs['field_name'])
        storage = get_storage(upload_to)
        if value:
            file_name = os.path.basename(value.name)
            file_url = storage.url(file_name)
        else:
            file_url = ""

        chunkSize = getattr(settings, 'ADMIN_RESUMABLE_CHUNKSIZE', "1*1024*1024")
        show_thumb = getattr(settings, 'ADMIN_RESUMABLE_SHOW_THUMB', False)
        context = {'name': name,
                   'value': value,
                   'id': attrs['id'],
                   'chunkSize': chunkSize,
                   'show_thumb': show_thumb,
                   'field_name': self.attrs['field_name'],
                   'content_type_id': self.attrs['content_type_id'],
                   'file_url': file_url}

        if not self.is_required:
            template_with_clear = '<span class="clearable-file-input">%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label></span>'
            substitutions = {}
            substitutions['clear_checkbox_id'] = attrs['id'] + "-clear-id"
            substitutions['clear_checkbox_name'] = attrs['id'] + "-clear"
            substitutions['clear_checkbox_label'] = self.clear_checkbox_label
            substitutions['clear'] = CheckboxInput().render(
                substitutions['clear_checkbox_name'],
                False,
                attrs={'id': substitutions['clear_checkbox_id']}
            )
            clear_checkbox = mark_safe(template_with_clear % substitutions)
            context.update({'clear_checkbox': clear_checkbox})
        return loader.render_to_string(self.template_name, context)

    def value_from_datadict(self, data, files, name):
        if not self.is_required and data.get("id_" + name + "-clear"):
            return False  # False signals to clear any existing value, as opposed to just None
        if data.get(name, None) in ['None', 'False']:
            return None
        return data.get(name, None)


class AdminResumableWidget(ResumableWidget):
    @property
    def media(self):
        js = ["resumable.js"]
        return forms.Media(js=[static("admin_resumable/js/%s" % path) for path in js])


class FormResumableFileField(FileField):
    widget = ResumableWidget


class FormAdminResumableFileField(FileField):
    widget = AdminResumableWidget

    def to_python(self, data):
        if self.required:
            if not data or data == "None":
                raise ValidationError(self.error_messages['empty'])
        return data


class ModelAdminResumableFileField(models.FileField):

    @property
    def orig_upload_to(self):
        return self.get_directory_name()

    def formfield(self, **kwargs):
        content_type_id = ContentType.objects.get_for_model(self.model).id
        defaults = {
            'form_class': FormAdminResumableFileField,
            'widget': AdminResumableWidget(attrs={
                'content_type_id': content_type_id,
                'field_name': self.name})
        }
        kwargs.update(defaults)
        return super(ModelAdminResumableFileField, self).formfield(**kwargs)
