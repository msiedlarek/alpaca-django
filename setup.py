# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(
    name='alpaca-django',
    version='0.1.0',
    description='Error reporter for Alpaca error aggregator.',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author=u'Mikołaj Siedlarek',
    author_email='m.siedlarek@nctz.net',
    url='https://github.com/msiedlarek/alpaca-django',
    keywords='web alpaca django error aggregation',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Django', 'requests']
)
