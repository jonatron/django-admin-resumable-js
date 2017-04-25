# -*- coding: utf-8 -*-
import fnmatch

from django.core.files.base import File

from admin_resumable.settings import ADMIN_RESUMABLE_CHUNKSUFFIX, \
    ADMIN_RESUMABLE_SIZE_PREFIX


class ResumableFile(object):
    def __init__(self, storage, params):
        self.storage = storage
        self.params = params
        self.chunk_suffix = ADMIN_RESUMABLE_CHUNKSUFFIX

    @property
    def chunk_exists(self):
        """
        Checks if the requested chunk exists.
        """
        return self.storage.exists(self.current_chunk_name) and \
               self.storage.size(self.current_chunk_name) == int(self.params.get('resumableCurrentChunkSize'))

    @property
    def chunk_names(self):
        """
        Iterates over all stored chunks.
        """
        pattern = '%s%s*' % (self.filename, self.chunk_suffix)
        filenames = sorted(self.storage.listdir('')[1])
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield filename

    @property
    def current_chunk_name(self):
        return "%s%s%s" % (
            self.filename,
            self.chunk_suffix,
            self.params.get('resumableChunkNumber').zfill(4)
        )

    def chunks(self):
        """
        Iterates over all stored chunks.
        """
        files = sorted(self.storage.listdir('')[1])
        for file in files:
            if fnmatch.fnmatch(file, '%s%s*' % (self.filename,
                                                self.chunk_suffix)):
                yield self.storage.open(file, 'rb').read()

    def delete_chunks(self):
        for chunk in self.chunk_names:
            self.storage.delete(chunk)

    @property
    def file(self):
        """
        Gets the complete file.
        """
        if not self.is_complete:
            raise Exception('Chunk(s) still missing')

        return self

    @property
    def filename(self):
        """
        Gets the filename.
        """
        filename = self.params.get('resumableFilename')
        if '/' in filename:
            raise Exception('Invalid filename')

        if ADMIN_RESUMABLE_SIZE_PREFIX:
            return "%s_%s" % (
                self.params.get('resumableTotalSize'),
                filename
            )

        return filename

    @property
    def name(self):
        return self.filename

    @property
    def is_complete(self):
        """
        Checks if all chunks are already stored.
        """
        return self.size >= int(self.params.get('resumableTotalSize'))

    def process_chunk(self, file):
        if self.storage.exists(self.current_chunk_name):
            self.storage.delete(self.current_chunk_name)
        # chunk filenames are not limited by the field's max_length
        self.storage.save(self.current_chunk_name, file)

    @property
    def size(self):
        """
        Sum of size of all chunks.
        """
        return sum(self.storage.size(n) for n in self.chunk_names)
