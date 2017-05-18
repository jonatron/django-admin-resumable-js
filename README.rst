django-admin-resumable-js
=========================

.. image:: https://api.travis-ci.org/jonatron/django-admin-resumable-js.svg?branch=master
   :target: https://travis-ci.org/jonatron/django-admin-resumable-js

django-admin-resumable-js is a django app to allow you to upload large files from within the django admin site.

Screenshot
----------

.. image:: https://github.com/jonatron/django-admin-resumable-js/raw/master/screenshot.png?raw=true


Installation
------------

* pip install django-admin-resumable-js
* Add ``admin_resumable`` to your ``INSTALLED_APPS``
* Add ``url(r'^admin_resumable/', include('admin_resumable.urls')),`` to your urls.py
* Add a model field eg: ``from admin_resumable.fields import ModelAdminResumableFileField``

::

    class Foo(models.Model):
        bar = models.CharField(max_length=200)
        foo = ModelAdminResumableFileField()



Optionally:

* Set ``ADMIN_RESUMABLE_CHUNKSIZE``, default is ``"1*1024*1024"``
* Set ``ADMIN_RESUMABLE_STORAGE``, default is ``'django.core.files.storage.FileSystemStorage'`` (must be a subclass of ``django.core.files.storage.FileSystemStorage``, or accept the ``location`` init parameter).  If you don't want the default FileSystemStorage behaviour of creating new files on the server with filenames appended with _1, _2, etc for consecutive uploads of the same file, then you could use this to set your storage class to something like https://djangosnippets.org/snippets/976/
* Set ``ADMIN_RESUMABLE_SHOW_THUMB``, default is False. Shows a thumbnail next to the "Currently:" link.

resumable.js settings:

* ``ADMIN_RESUMABLE_PARALLEL``, default: 3
* ``ADMIN_RESUMABLE_FIRSTLAST``, default: ``False``
* ``ADMIN_RESUMABLE_RETRIES``, default: ``None``


South
-----

If you use South for migration, then put this at the top of your models.py file to help South introspect your ``ModelAdminResumableFileField``:

::

    from south.modelsinspector import add_introspection_rules

    add_introspection_rules([], [
        r'^admin_resumable\.fields\.ModelAdminResumableFileField'])


Versions
--------

1.0: First PyPI release

1.1: Bug fix [1]

1.2: Django 1.9 Compatibility

2.0: Added upload_to

2.0.fdemmer: prerelease/fork versions with a lot of rewrites

* updated resumable.js to 1.0.3
* add resumable.js configuration variables like ADMIN_RESUMABLE_PARALLEL, ...
* remove ADMIN_RESUMABLE_SUBDIR, use a different storage to customize that
* rewrite the upload view as CBV
* change path of upload view to upload/
* show value of FileField rather than the URL in the widget
* fix to respect max_length of FileField
* fix in render() to work when value is a string


[1] Django silently truncates incomplete chunks, due to the way the multipart
parser works: https://github.com/django/django/blob/master/django/http/multipartparser.py
This could result in a file being unable to be uploaded, or a corrupt file,
depending on the situation.


Compatibility
-------------

1.2:
{py27,py32,py33,py34,py35}-django{1.6,1.7,1.8,1.9}.
python 3.2 and 3.3 supported up to django 1.8.

2.0:
{py27,py34,py35}-django{1.8,1.9,1.10,1.11}

Thanks to
---------

Resumable.js https://github.com/23/resumable.js

django-resumable https://github.com/jeanphix/django-resumable
