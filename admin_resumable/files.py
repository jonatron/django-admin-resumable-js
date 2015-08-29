# -*- coding: utf-8 -*-
import fnmatch

from django.core.files.base import File


class ResumableFile(object):
    def __init__(self, storage, kwargs):
        self.storage = storage
        self.kwargs = kwargs
        self.chunk_suffix = "_part_"

    @property
    def chunk_exists(self):
        """Checks if the requested chunk exists.
        """
        return self.storage.exists(self.current_chunk_name) and \
               self.storage.size(self.current_chunk_name) == int(self.kwargs.get('resumableCurrentChunkSize'))

    @property
    def chunk_names(self):
        """Iterates over all stored chunks.
        """
        chunks = []
        files = sorted(self.storage.listdir('')[1])
        for file in files:
            if fnmatch.fnmatch(file, '%s%s*' % (self.filename,
                                                self.chunk_suffix)):
                chunks.append(file)
        return chunks

    @property
    def current_chunk_name(self):
        return "%s%s%s" % (
            self.filename,
            self.chunk_suffix,
            self.kwargs.get('resumableChunkNumber').zfill(4)
        )

    def chunks(self):
        """Iterates over all stored chunks.
        """
        chunks = []
        files = sorted(self.storage.listdir('')[1])
        for file in files:
            if fnmatch.fnmatch(file, '%s%s*' % (self.filename,
                                                self.chunk_suffix)):
                yield self.storage.open(file, 'rb').read()

    def delete_chunks(self):
        [self.storage.delete(chunk) for chunk in self.chunk_names]

    @property
    def file(self):
        """Gets the complete file.
        """
        if not self.is_complete:
            raise Exception('Chunk(s) still missing')

        return self

    @property
    def filename(self):
        """Gets the filename."""
        filename = self.kwargs.get('resumableFilename')
        if '/' in filename:
            raise Exception('Invalid filename')
        return "%s_%s" % (
            self.kwargs.get('resumableTotalSize'),
            filename
        )

    @property
    def is_complete(self):
        """Checks if all chunks are already stored.
        """
        return int(self.kwargs.get('resumableTotalSize')) == self.size

    def process_chunk(self, file):
        if self.storage.exists(self.current_chunk_name):
            self.storage.delete(self.current_chunk_name)
        self.storage.save(self.current_chunk_name, file)

    @property
    def size(self):
        """Gets chunks size.
        """
        size = 0
        for chunk in self.chunk_names:
            size += self.storage.size(chunk)
        return size
