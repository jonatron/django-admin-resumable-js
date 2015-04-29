import pytest
import os
from selenium import webdriver

browsers = {
    'firefox': webdriver.Firefox,
    #'chrome': webdriver.Chrome,
}


@pytest.fixture(scope='session',
                params=browsers.keys())
def driver(request):
    if 'DISPLAY' not in os.environ:
        pytest.skip('Test requires display server (export DISPLAY)')

    b = browsers[request.param]()

    request.addfinalizer(lambda *args: b.quit())

    return b


def pytest_configure():
    import django
    from django.conf import settings

    settings.configure(
        DEBUG=False,
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        SITE_ID=1,
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        USE_L10N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        TEMPLATE_LOADERS=(
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'admin_resumable',
            'tests',
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ),
        MEDIA_ROOT=os.path.join(os.path.dirname(__file__), 'media')
    )
    print settings.MEDIA_ROOT
    try:
        import django
        django.setup()
    except AttributeError:
        pass
