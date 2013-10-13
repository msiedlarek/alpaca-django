# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup, find_packages

from alpaca_django import __version__ as alpaca_django_version


here = os.path.abspath(os.path.dirname(__file__))


readme_path = os.path.join(here, 'README.txt')
with codecs.open(readme_path, 'r', encoding='utf-8') as file:
    readme = file.read()


requirements = [
    'django',
    'msgpack-python',
    'pyzmq',
]


setup(
    name='alpaca-django',
    version=alpaca_django_version,
    description='Alpaca error logger for Django applications.',
    long_description=readme,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: Apache Software License',
    ],
    author='Mikołaj Siedlarek',
    author_email='msiedlarek@nctz.net',
    url='https://github.com/msiedlarek/alpaca-django',
    keywords='web alpaca error exception logging monitoring django',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements
)
