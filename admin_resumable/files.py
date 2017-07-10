# -*- coding: utf-8 -*-
import fnmatch
import tempfile


class ResumableFile(object):
    def __init__(self, chunk_storage, kwargs):
        self.chunk_storage = chunk_storage
        self.kwargs = kwargs
        self.chunk_suffix = "_part_"

    @property
    def chunk_exists(self):
        """
        Checks if the requested chunk exists.
        """
        return self.chunk_storage.exists(self.current_chunk_name) and \
               self.chunk_storage.size(self.current_chunk_name) == int(self.kwargs.get('resumableCurrentChunkSize'))

    @property
    def chunk_names(self):
        """
        Iterates over all stored chunks.
        """
        chunks = []
        files = sorted(self.chunk_storage.listdir('')[1])
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
        """
        Iterates over all stored chunks.
        """
        files = sorted(self.chunk_storage.listdir('')[1])
        for file in files:
            if fnmatch.fnmatch(file, '%s%s*' % (self.filename,
                                                self.chunk_suffix)):
                yield self.chunk_storage.open(file, 'rb').read()

    def delete_chunks(self):
        [self.chunk_storage.delete(chunk) for chunk in self.chunk_names]

    @property
    def file(self):
        """
        Merges file and returns its file pointer.
        """
        if not self.is_complete:
            raise Exception('Chunk(s) still missing')
        outfile = tempfile.NamedTemporaryFile("w+b")
        for chunk in self.chunk_names:
            outfile.write(self.chunk_storage.open(chunk).read())
        return outfile

    @property
    def filename(self):
        """
        Gets the filename.
        """
        filename = self.kwargs.get('resumableFilename')
        if '/' in filename:
            raise Exception('Invalid filename')
        value = "%s_%s" % (self.kwargs.get('resumableTotalSize'), filename)
        return value

    @property
    def is_complete(self):
        """
        Checks if all chunks are already stored.
        """
        return int(self.kwargs.get('resumableTotalSize')) == self.size

    def process_chunk(self, file):
        if self.chunk_storage.exists(self.current_chunk_name):
            self.chunk_storage.delete(self.current_chunk_name)
        self.chunk_storage.save(self.current_chunk_name, file)

    @property
    def size(self):
        """
        Gets size of all chunks combined.
        """
        size = 0
        for chunk in self.chunk_names:
            size += self.chunk_storage.size(chunk)
        return size
