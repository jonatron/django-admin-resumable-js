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


Todo
----

* Reorganise Code
* Make installable
* Testing
* Multiple file uploads?

Thanks to
---------

Resumable.js https://github.com/23/resumable.js

django-resumable https://github.com/jeanphix/django-resumable
