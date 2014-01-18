from django.forms.widgets import FileInput
from django.forms import forms
from django.db import models
from django.templatetags.static import static
from django.template import loader
from django.forms.fields import FileField
from django.core.exceptions import ValidationError

class ResumableWidget(FileInput):
    template_name = 'admin_resumable/file_input.html'

    def render(self, name, value, attrs=None, **kwargs):
        context = {'name': name, 'value': value, 'id': attrs['id']}
        return loader.render_to_string(self.template_name, context)

    def value_from_datadict(self, data, files, name):
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
        if not data or data == "None":
            raise ValidationError(self.error_messages['empty'])
        return data

class ModelAdminResumableFileField(models.FileField):
    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        super(ModelAdminResumableFileField, self).__init__(verbose_name, name, 'unused', **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': FormAdminResumableFileField, 'widget': AdminResumableWidget}
        kwargs.update(defaults)
        return super(ModelAdminResumableFileField, self).formfield(**kwargs)