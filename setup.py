import os
from setuptools import setup, find_packages

from alpaca_django import __version__ as alpaca_django_version


here = os.path.abspath(os.path.dirname(__file__))


requirements = [
    'django',
    'msgpack-python',
    'pyzmq',
]


setup(
    name='alpaca-django',
    version=alpaca_django_version,
    description='',
    long_description='',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python 3',
        'Framework :: Django',
        'Topic :: Internet :: WWW/HTTP',
    ],
    author='Mikołaj Siedlarek',
    author_email='m.siedlarek@nctz.net',
    url='https://github.com/msiedlarek/alpaca-django',
    keywords='web alpaca error exception logging monitoring django',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements
)
