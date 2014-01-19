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

class ResumableWidget(FileInput):
    template_name = 'admin_resumable/file_input.html'
    clear_checkbox_label = ugettext_lazy('Clear')

    def render(self, name, value, attrs=None, **kwargs):
        chunkSize = getattr(settings, 'ADMIN_RESUMABLE_CHUNKSIZE', "1*1024*1024")
        context = {'name': name, 'value': value, 'id': attrs['id'], 'chunkSize': chunkSize}
        if not self.is_required:
            template_with_clear = '<span class="clearable-file-input">%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label></span>'
            substitutions = {}
            substitutions['clear_checkbox_id'] = attrs['id'] + "-clear-id"
            substitutions['clear_checkbox_name'] = attrs['id'] + "-clear"
            substitutions['clear_checkbox_label'] = self.clear_checkbox_label
            substitutions['clear'] = CheckboxInput().render(substitutions['clear_checkbox_name'],
                False, attrs={'id': substitutions['clear_checkbox_id']})
            clear_checkbox = mark_safe(template_with_clear % substitutions)
            
            context.update({'clear_checkbox': clear_checkbox})
        return loader.render_to_string(self.template_name, context)

    def value_from_datadict(self, data, files, name):
        if not self.is_required and data.get("id_" + name + "-clear"):
            return False # False signals to clear any existing value, as opposed to just None
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