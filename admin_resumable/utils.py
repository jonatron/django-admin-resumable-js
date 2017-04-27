import os

from django.contrib.contenttypes.models import ContentType


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def get_model_field(request):
    """
    Determine the model field for the uploaded file/chunk using the
    'content_type_id' and 'field_name' request parameters.
    """
    params = request.GET
    if request.method == 'POST':
        params = request.POST

    ctype = ContentType.objects.get_for_id(params['content_type_id'])
    # noinspection PyProtectedMember
    return ctype.model_class()._meta.get_field(params['field_name'])
