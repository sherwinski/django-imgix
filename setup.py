import os
from setuptools import setup, find_packages
from django_imgix.templatetags._version import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-imgix',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license='ISC',
    description='An app for integrating imgix into Django sites',
    long_description=README,
    url='https://github.com/imgix/django-imgix',
    author='Pancentric Ltd',
    author_email='devops@pancentric.com',
    maintainer='imgix',
    maintainer_email='sdk@imgix.com',
    install_requires=[
        'django==3.2',
        'imgix==3.2.1',
        'six==1.15.0'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
