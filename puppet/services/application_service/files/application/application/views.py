import sys

import django


class DummyException(Exception):
    pass


def home(request):
    raise DummyException(
        "Dummy error from Django {django_version} on Python"
        " {python_version}.".format(
            django_version=django.get_version(),
            python_version='.'.join(map(str, sys.version_info[:3]))
        )
    )
