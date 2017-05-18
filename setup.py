import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-admin-resumable-js',
    version='2.0+fdemmer.3',
    packages=['admin_resumable'],
    include_package_data=True,
    package_data={
        'admin_resumable': [
            'templates/admin_resumable/file_input.html',
            'static/admin_resumable/js/resumable.js',
        ]
    },
    license='MIT License',
    description='A Django app for the uploading of large files from the django admin site.',
    long_description=README,
    url='https://github.com/fdemmer/django-admin-resumable-js',
    author='Florian Demmer',
    author_email='fdemmer@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
