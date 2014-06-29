django-admin-resumable-js
=========================

django-admin-resumable-js is a django app to allow you to upload large files from within the django admin site.

Screenshot
----------
![Image](screenshot.png?raw=true)


Installation
------------

* Add ```admin_resumable``` to your ```INSTALLED_APPS```
* Add ```url(r'^admin_resumable/', include('admin_resumable.urls')),``` to your urls.py
* Add a model field eg:
```from admin_resumable.fields import ModelAdminResumableFileField```

```python
class Foo(models.Model):
  bar = models.CharField(max_length=200)
  foo = ModelAdminResumableFileField()
```

Optionally:

* Set ``ADMIN_RESUMABLE_SUBDIR``, default is ``'admin_uploaded'``
* Set ``ADMIN_RESUMABLE_CHUNKSIZE``, default is ``"1*1024*1024"``


South
-----

If you use South for migration, then put this at the top of your models.py file to help South introspect your ``ModelAdminResumableFileField``:

```python
from south.modelsinspector import add_introspection_rules

add_introspection_rules([], [
    r'^admin_resumable\.fields\.ModelAdminResumableFileField'])


Todo
----

* Testing

Thanks to
---------

Resumable.js https://github.com/23/resumable.js

django-resumable https://github.com/jeanphix/django-resumable
