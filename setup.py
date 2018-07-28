#from __future__ import print_function
import ast
import os
import sys
import codecs
import subprocess
from fnmatch import fnmatchcase
from distutils.util import convert_path
from setuptools import setup, find_packages


def find_version(*parts):
    from workon.version import __version__
    return "{ver}".format(ver=__version__)

def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()



# Provided as an attribute, so you can append to these instead
# of replicating them:
# standard_exclude = ('*.py', '*.pyc', '*$py.class', '*~', '.*', '*.bak')
# standard_exclude_directories = ('.*', 'CVS', '_darcs', './build',
#                                 './dist', 'EGG-INFO', '*.egg-info')

setup(
    name='django-workon',
    version=find_version(),
    description='Django extensions packages',
    long_description=read('README.rst'),
    author='Autrusseau Damien',
    author_email='autrusseau.damien@gmail.com',
    url='http://github.com/workon-io/django-workon',
    packages=find_packages(exclude=('tests',)),
    zip_safe=False,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    # test_suite='runtests.runtests',
    install_requires=[
        'django>=2.0.0,<3.0.0',
        'premailer>=3.1.1,<4.0.0',
    ],
)
