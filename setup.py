# -*- coding: utf-8; -*-
import os
from codecs import open

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

version = '0.1.1'

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    author='Michał Krzywkowski',
    author_email='k.michal@zoho.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Email',
        'Topic :: Internet',
    ],
    description='Watch Maildir for incoming mail and display notifications',
    download_url='https://github.com/mkcms/maildirwatch/archive/v{}.tar.gz'.
    format(version),
    entry_points={'console_scripts': {'maildirwatch = maildirwatch:main'}},
    include_package_data=True,
    install_requires=['PyGObject'],
    license='GPLv3',
    long_description=long_description,
    name='maildirwatch',
    py_modules=['maildirwatch'],
    url='https://github.com/mkcms/maildirwatch',
    version=version,
)
