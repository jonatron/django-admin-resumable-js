#from django.shortcuts import render, redirect
import os
from django.conf import settings
from django.http import HttpResponse
from admin_resumable.files import ResumableFile
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def get_chunks_subdir():
    return getattr(settings, 'ADMIN_RESUMABLE_SUBDIR', 'admin_uploaded')

def get_chunks_dir():
    chunks_subdir = get_chunks_subdir()
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root:
        raise ImproperlyConfigured(
            'You must set settings.MEDIA_ROOT')
    chunks_dir = os.path.join(media_root, chunks_subdir)
    ensure_dir(chunks_dir)
    return chunks_dir

def admin_resumable(request):
    chunks_dir = get_chunks_dir()
    storage = FileSystemStorage(location=chunks_dir)
    if request.method == 'POST':
        chunk = request.FILES.get('file')
        r = ResumableFile(storage, request.POST)
        if r.chunk_exists:
            return HttpResponse('chunk already exists')
        r.process_chunk(chunk)
        if r.is_complete:
            actual_filename = storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(get_chunks_subdir() + "/" + actual_filename)
        return HttpResponse()
    elif request.method == 'GET':
        r = ResumableFile(storage, request.GET)
        if not r.chunk_exists:
            return HttpResponse('chunk not found', status=404)
        if r.is_complete:
            actual_filename = storage.save(r.filename, r.file)
            r.delete_chunks()
            return HttpResponse(get_chunks_subdir() + "/" + actual_filename)
        return HttpResponse('chunk already exists')