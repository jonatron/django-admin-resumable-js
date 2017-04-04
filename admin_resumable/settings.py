from django.conf import settings

# resumable.js settings

# chunkSize
ADMIN_RESUMABLE_CHUNKSIZE = getattr(
    settings,
    'ADMIN_RESUMABLE_CHUNKSIZE',
    '1*1024*1024'
)
# simultaneousUploads
ADMIN_RESUMABLE_PARALLEL = getattr(
    settings,
    'ADMIN_RESUMABLE_PARALLEL',
    3
)
# prioritizeFirstAndLastChunk
ADMIN_RESUMABLE_FIRSTLAST = getattr(
    settings,
    'ADMIN_RESUMABLE_FIRSTLAST',
    False
)
# maxChunkRetries
ADMIN_RESUMABLE_RETRIES = getattr(
    settings,
    'ADMIN_RESUMABLE_RETRIES',
    None
)

# widget settings
ADMIN_RESUMABLE_SHOW_THUMB = getattr(
    settings,
    'ADMIN_RESUMABLE_SHOW_THUMB',
    False
)

# others
ADMIN_RESUMABLE_CHUNKSUFFIX = getattr(
    settings,
    'ADMIN_RESUMABLE_CHUNKSUFFIX',
    '_part_'
)
